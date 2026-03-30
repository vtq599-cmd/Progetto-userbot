from telethon import events
from telethon.tl.types import Channel, Chat, User

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}chatinfo$", outgoing=True))
    async def chatinfo_handler(event):
        chat = await event.get_chat()
        chat_id = event.chat_id

        if isinstance(chat, User):
            text = (
                f"👤 **Личный чат**\n\n"
                f"**Имя:** {chat.first_name or ''} {chat.last_name or ''}\n"
                f"**Username:** @{chat.username or 'нет'}\n"
                f"**ID:** `{chat.id}`\n"
                f"**Бот:** {'Да' if chat.bot else 'Нет'}"
            )
        elif isinstance(chat, (Channel, Chat)):
            members = getattr(chat, "participants_count", None) or getattr(chat, "members_count", "?")
            is_channel = isinstance(chat, Channel) and chat.broadcast
            kind = "📢 Канал" if is_channel else "👥 Группа/Супергруппа"
            text = (
                f"{kind}\n\n"
                f"**Название:** {chat.title}\n"
                f"**ID:** `{chat_id}`\n"
                f"**Username:** @{chat.username or 'нет'}\n"
                f"**Участников:** {members}\n"
                f"**Верифицирован:** {'✅' if getattr(chat, 'verified', False) else '❌'}\n"
                f"**Scam:** {'⚠️ Да' if getattr(chat, 'scam', False) else '❌'}"
            )
        else:
            text = f"**ID чата:** `{chat_id}`"

        await event.edit(text)
