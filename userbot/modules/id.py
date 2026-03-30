from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}id", outgoing=True))
    async def id_handler(event):
        chat = await event.get_chat()
        reply = await event.get_reply_message()

        lines = [f"**🆔 Chat ID:** `{event.chat_id}`"]
        if hasattr(chat, "title"):
            lines.append(f"**📛 Название:** {chat.title}")
        if reply and reply.sender_id:
            sender = reply.sender
            lines.append(f"\n**👤 Пользователь:** `{reply.sender_id}`")
            if sender and hasattr(sender, "first_name"):
                lines.append(f"**Имя:** {sender.first_name or ''} {sender.last_name or ''}")
                if sender.username:
                    lines.append(f"**Username:** @{sender.username}")

        await event.edit("\n".join(lines))
