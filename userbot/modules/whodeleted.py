import re
import asyncio

from telethon import events
from telethon.tl.functions.channels import GetAdminLogRequest
from telethon.tl.types import ChannelAdminLogEventsFilter

from modules.history import message_link


_active = False


def register(client, prefix):
    global _active

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}whodeleted(?:\s+(on|off))?$", outgoing=True))
    async def command(event):
        global _active
        action = (event.pattern_match.group(1) or "").lower()
        if action == "on":
            _active = True
        elif action == "off":
            _active = False
        status = "включён" if _active else "выключен"
        await event.edit(f"🗑 WhoDeleted: **{status}**")

    @client.on(events.MessageDeleted())
    async def deleted(event):
        if not _active or event.chat_id is None:
            return
        await asyncio.sleep(0.15)
        me = await client.get_me()
        for message_id in event.deleted_ids:
            record = {
                "message_id": message_id,
                "sender_id": None,
                "text": "Содержимое недоступно в локальном кэше",
            }
            try:
                from modules.history import get_deleted
                records = get_deleted(event.chat_id, 100)
                record = next(
                    (item for item in reversed(records) if item["message_id"] == message_id),
                    record,
                )
            except Exception:
                pass
            deleter = "неизвестно (Telegram не сообщил)"
            try:
                log = await client(
                    GetAdminLogRequest(
                        channel=await event.get_input_chat(),
                        q="",
                        max_id=0,
                        min_id=0,
                        limit=50,
                        events_filter=ChannelAdminLogEventsFilter(delete=True),
                    )
                )
                for entry in log.events:
                    deleted_message = getattr(entry.action, "message", None)
                    if getattr(deleted_message, "id", None) == message_id:
                        actor = await client.get_entity(entry.user_id)
                        deleter = (
                            f"{getattr(actor, 'first_name', '') or ''} "
                            f"{getattr(actor, 'last_name', '') or ''}".strip()
                            or str(entry.user_id)
                        )
                        break
            except Exception:
                pass
            link = await message_link(client, event.chat_id, record["message_id"])
            await client.send_message(
                me.id,
                f"🗑 **Удалено сообщение**\n"
                f"👤 Автор ID: `{record.get('sender_id') or 'неизвестно'}`\n"
                f"🧹 Удалил: {deleter}\n"
                f"💬 {record['text'][:500]}\n"
                f"🔗 {link or 'ссылка недоступна'}",
                parse_mode=None,
            )