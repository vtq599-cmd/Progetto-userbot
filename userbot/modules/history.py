from collections import defaultdict
from datetime import datetime, timezone
import asyncio
import json
from pathlib import Path

from telethon import events


MAX_PER_CHAT = 1000
MAX_TOTAL_MESSAGES = 3000
MAX_DELETED_TOTAL = 1000
_messages = defaultdict(dict)
_versions = defaultdict(list)
_deleted = defaultdict(list)
_store_path = Path(__file__).resolve().parents[1] / "history.json"
_save_task = None


def _key(chat_id, message_id):
    return f"{chat_id}:{message_id}"


def _trim_cache():
    all_messages = [
        (record["date"], chat_id, message_id)
        for chat_id, records in _messages.items()
        for message_id, record in records.items()
    ]
    while len(all_messages) > MAX_TOTAL_MESSAGES:
        _, chat_id, message_id = min(all_messages)
        _messages[chat_id].pop(message_id, None)
        _versions.pop(_key(chat_id, message_id), None)
        all_messages.remove(min(all_messages))

    all_deleted = [
        (record["date"], chat_id, record["message_id"])
        for chat_id, records in _deleted.items()
        for record in records
    ]
    while len(all_deleted) > MAX_DELETED_TOTAL:
        _, chat_id, message_id = min(all_deleted)
        _deleted[chat_id] = [
            record for record in _deleted[chat_id]
            if record["message_id"] != message_id
        ]
        all_deleted.remove(min(all_deleted))


def _load():
    try:
        state = json.loads(_store_path.read_text(encoding="utf-8"))
        for record in state.get("messages", []):
            _messages[int(record["chat_id"])][int(record["message_id"])] = record
        for key, values in state.get("versions", {}).items():
            _versions[key] = values[-30:]
        for record in state.get("deleted", []):
            _deleted[int(record["chat_id"])].append(record)
        for chat_id in list(_messages):
            if len(_messages[chat_id]) > MAX_PER_CHAT:
                keep = sorted(_messages[chat_id])[-MAX_PER_CHAT:]
                _messages[chat_id] = {mid: _messages[chat_id][mid] for mid in keep}
        for chat_id in list(_deleted):
            _deleted[chat_id] = _deleted[chat_id][-100:]
        _trim_cache()
    except (OSError, ValueError, TypeError, KeyError):
        return


def _save():
    state = {
        "messages": [
            record
            for chat_messages in _messages.values()
            for record in chat_messages.values()
        ],
        "versions": {key: values[-30:] for key, values in _versions.items()},
        "deleted": [
            record
            for chat_deleted in _deleted.values()
            for record in chat_deleted[-100:]
        ],
    }
    try:
        tmp = _store_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_store_path)
    except OSError:
        pass


async def _delayed_save():
    global _save_task
    await asyncio.sleep(2)
    _save()
    _save_task = None


def _schedule_save():
    global _save_task
    if _save_task is None or _save_task.done():
        _save_task = asyncio.create_task(_delayed_save())


_load()


def _record(message):
    return {
        "chat_id": message.chat_id,
        "message_id": message.id,
        "sender_id": message.sender_id,
        "text": (message.text or "[медиа]")[:4096],
        "date": (
            message.date.astimezone(timezone.utc).isoformat()
            if message.date
            else datetime.now(timezone.utc).isoformat()
        ),
    }


def remember(message):
    if not message or message.chat_id is None or not message.id:
        return

    key = _key(message.chat_id, message.id)
    current = _record(message)
    previous = _messages[message.chat_id].get(message.id)
    if previous and previous["text"] != current["text"]:
        versions = _versions[key]
        if not versions:
            versions.append(previous)
        versions.append(current)
    elif key not in _versions:
        _versions[key] = [current]

    _messages[message.chat_id][message.id] = current
    if len(_messages[message.chat_id]) > MAX_PER_CHAT:
        oldest = min(_messages[message.chat_id])
        _messages[message.chat_id].pop(oldest, None)
    _trim_cache()


def get_versions(chat_id, message_id):
    key = _key(chat_id, message_id)
    values = list(_versions.get(key, []))
    current = _messages.get(chat_id, {}).get(message_id)
    if current and (not values or values[-1]["text"] != current["text"]):
        values.append(current)
    return values


def get_deleted(chat_id, limit=10):
    return list(_deleted.get(chat_id, []))[-limit:]


def first_cached(chat_id, sender_id=None):
    values = list(_messages.get(chat_id, {}).values())
    values.extend(_deleted.get(chat_id, []))
    if sender_id is not None:
        values = [item for item in values if item["sender_id"] == sender_id]
    return min(values, key=lambda item: item["message_id"]) if values else None


async def message_link(client, chat_id, message_id):
    try:
        chat = await client.get_entity(chat_id)
    except Exception:
        chat = None

    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}/{message_id}"

    chat_text = str(chat_id)
    if chat_text.startswith("-100"):
        return f"https://t.me/c/{chat_text[4:]}/{message_id}"
    return None


def register(client, prefix):
    @client.on(events.NewMessage)
    async def cache_new_message(event):
        remember(event.message)
        _schedule_save()

    @client.on(events.MessageEdited)
    async def cache_edited_message(event):
        remember(event.message)
        _schedule_save()

    @client.on(events.MessageDeleted())
    async def remember_deleted_messages(event):
        chat_id = event.chat_id
        if chat_id is None:
            return
        for message_id in event.deleted_ids:
            record = _messages.get(chat_id, {}).pop(message_id, None)
            if record:
                _deleted[chat_id].append(record)
        _deleted[chat_id] = _deleted[chat_id][-100:]
        _trim_cache()
        _schedule_save()