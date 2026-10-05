from datetime import timezone
import re
from zoneinfo import ZoneInfo

from telethon import events


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}link$", outgoing=True))
    async def link_handler(event):
        reply = await event.get_reply_message()
        target = reply or event
        chat = await event.get_chat()
        username = getattr(chat, "username", None)
        chat_id = str(event.chat_id)
        if username:
            link = f"https://t.me/{username}/{target.id}"
        elif chat_id.startswith("-100"):
            link = f"https://t.me/c/{chat_id[4:]}/{target.id}"
        else:
            return await event.edit("❌ Для этого чата Telegram не создаёт ссылку.")
        date = target.date.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Europe/Moscow"))
        await event.edit(
            f"🔗 {link}\n"
            f"🕐 {date.strftime('%d.%m.%Y %H:%M МСК')}\n"
            f"💬 {(target.text or '[медиа]')[:120]}"
        )