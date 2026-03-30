from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}link$", outgoing=True))
    async def link_handler(event):
        reply = await event.get_reply_message()
        target = reply if reply else event

        try:
            chat = await event.get_chat()
            username = getattr(chat, "username", None)
            chat_id = event.chat_id
            msg_id = target.id

            if username:
                link = f"https://t.me/{username}/{msg_id}"
                chat_name = getattr(chat, "title", username)
            elif str(chat_id).startswith("-100"):
                pure_id = str(chat_id).replace("-100", "")
                link = f"https://t.me/c/{pure_id}/{msg_id}"
                chat_name = getattr(chat, "title", str(chat_id))
            else:
                return await event.edit(
                    "❌ Ссылку можно получить только в публичных группах/каналах"
                )

            sender = await target.get_sender()
            sender_name = ""
            if sender:
                first = getattr(sender, "first_name", "") or ""
                last = getattr(sender, "last_name", "") or ""
                sender_name = f"{first} {last}".strip()

            date_str = target.date.strftime("%d.%m.%Y %H:%M")
            preview = (target.text or "[медиа]")[:80]

            lines = [f"🔗 **Ссылка на сообщение**\n", f"💬 **Чат:** {chat_name}"]
            if sender_name:
                lines.append(f"👤 **Автор:** {sender_name}")
            lines += [f"📅 **Дата:** {date_str}", f"📝 **Текст:** {preview}\n", f"🔗 {link}"]

            await event.edit("\n".join(lines))

        except Exception as e:
            await event.edit(f"❌ {e}")
