from telethon import events

_active = False

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}fspy ?(.*)", outgoing=True))
    async def fspy_cmd(event):
        global _active
        arg = event.pattern_match.group(1).strip().lower()

        if arg == "on":
            if _active:
                return await event.edit("👁 ForwardSpy уже включён")
            _active = True
            await event.edit("👁 **ForwardSpy включён**\nБуду следить за пересылками твоих сообщений")
        elif arg == "off":
            if not _active:
                return await event.edit("😴 ForwardSpy уже выключён")
            _active = False
            await event.edit("😴 **ForwardSpy выключён**")
        else:
            status = "включён 👁" if _active else "выключён 😴"
            await event.edit(f"ℹ️ ForwardSpy: **{status}**\n`.fspy on` / `.fspy off`")

    @client.on(events.NewMessage(incoming=True))
    async def fspy_watcher(event):
        if not _active or event.out:
            return
        try:
            fwd = event.forward
            if not fwd:
                return

            fwd_from = fwd.from_id
            if not fwd_from:
                return

            me = await client.get_me()
            from_id = getattr(fwd_from, "user_id", None)
            if from_id != me.id:
                return

            sender = await event.get_sender()
            if not sender:
                return

            s_first = getattr(sender, "first_name", "") or ""
            s_last = getattr(sender, "last_name", "") or ""
            s_name = f"{s_first} {s_last}".strip()
            s_username = f"@{sender.username}" if getattr(sender, "username", None) else ""

            chat = await event.get_chat()
            chat_name = getattr(chat, "title", None) or "Личные сообщения"
            chat_username = f"@{chat.username}" if getattr(chat, "username", None) else ""

            orig_text = (event.text or "[медиа]")[:100]

            await client.send_message(
                me.id,
                f"📤 **Твоё сообщение переслали!**\n\n"
                f"👤 **Кто:** {s_name} {s_username}\n"
                f"💬 **Куда:** {chat_name} {chat_username}\n"
                f"📝 **Сообщение:** _{orig_text}_"
            )
        except Exception:
            pass
