from datetime import datetime, timezone
import re

from telethon import events


def name_of(user):
    if not user:
        return "неизвестно"
    name = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
    return name or str(getattr(user, "id", "неизвестно"))


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}(?:id|ui)$", outgoing=True))
    async def user_info(event):
        reply = await event.get_reply_message()
        user = await reply.get_sender() if reply else await event.get_sender()
        username = f"@{user.username}" if getattr(user, "username", None) else "нет"
        await event.edit(
            f"👤 **{name_of(user)}**\n"
            f"🆔 `{user.id}`\n"
            f"🔗 {username}"
        )

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}chatinfo$", outgoing=True))
    async def chat_info(event):
        chat = await event.get_chat()
        username = f"@{chat.username}" if getattr(chat, "username", None) else "нет"
        await event.edit(
            f"💬 **{getattr(chat, 'title', None) or name_of(chat)}**\n"
            f"🆔 `{event.chat_id}`\n"
            f"🔗 {username}"
        )

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}ls$", outgoing=True))
    async def last_seen(event):
        reply = await event.get_reply_message()
        user = await reply.get_sender() if reply else await event.get_sender()
        status = getattr(user, "status", None)
        if not status:
            return await event.edit(f"👤 **{name_of(user)}**\nСтатус скрыт.")
        was_online = getattr(status, "was_online", None)
        if was_online:
            when = was_online.astimezone(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
            text = f"Последний онлайн: `{when}`"
        else:
            text = f"Статус: `{type(status).__name__}`"
        await event.edit(f"👤 **{name_of(user)}**\n{text}")