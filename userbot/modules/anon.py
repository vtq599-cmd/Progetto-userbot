from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}anon ?(.*)", outgoing=True))
    async def anon_handler(event):
        args = event.pattern_match.group(1).strip().split(None, 1)

        if len(args) < 2:
            await event.edit(
                "❌ **Использование:**\n"
                "`.anon @username Привет!`\n"
                "`.anon -1001234567890 Текст`"
            )
            return

        target_raw, text = args[0], args[1]

        try:
            try:
                target = int(target_raw)
            except ValueError:
                target = target_raw

            entity = await client.get_entity(target)
            await client.send_message(entity, f"📨 **Анонимное сообщение:**\n\n{text}")
            await event.edit("✅ **Сообщение отправлено**")

        except Exception as e:
            await event.edit(f"❌ {e}")
