from telethon import events

_active = False
_cache = {}

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}whodeleted ?(.*)", outgoing=True))
    async def whodeleted_cmd(event):
        global _active
        arg = event.pattern_match.group(1).strip().lower()
        if arg == "on":
            _active = True
            await event.edit("✅ **WhoDeleted включён**")
        elif arg == "off":
            _active = False
            await event.edit("❌ **WhoDeleted выключён**")
        else:
            status = "включён ✅" if _active else "выключён ❌"
            await event.edit(f"ℹ️ Статус: **{status}**")

    @client.on(events.NewMessage(incoming=True))
    async def cache_messages(event):
        if not _active:
            return
        try:
            chat_id = event.chat_id
            if chat_id not in _cache:
                _cache[chat_id] = {}
            sender_name = None
            if event.sender:
                sender_name = (
                    f"{getattr(event.sender, 'first_name', '') or ''} "
                    f"{getattr(event.sender, 'last_name', '') or ''}".strip()
                )
            _cache[chat_id][event.id] = {
                "text": event.text or "[медиа]",
                "sender_id": event.sender_id,
                "sender": sender_name,
            }
        except Exception:
            pass

    @client.on(events.MessageDeleted())
    async def on_deleted(event):
        if not _active:
            return
        try:
            chat_id = event.chat_id
            if not chat_id or chat_id not in _cache:
                return
            for msg_id in event.deleted_ids:
                cached = _cache.get(chat_id, {}).pop(msg_id, None)
                if not cached:
                    continue
                sender = cached["sender"] or f"ID:{cached['sender_id']}"
                text = (cached["text"] or "")[:200]
                me = await client.get_me()
                await client.send_message(
                    me.id,
                    f"🗑 **Удалённое сообщение**\n\n"
                    f"👤 **Автор:** {sender}\n"
                    f"💬 **Текст:** `{text}`\n"
                    f"📍 **Чат:** `{chat_id}`"
                )
        except Exception:
            pass
