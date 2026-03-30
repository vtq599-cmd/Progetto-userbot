from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}ff ?(.*)", outgoing=True))
    async def ff_handler(event):
        args = event.pattern_match.group(1).strip().split(None, 1)

        if len(args) < 2:
            await event.edit(
                "❌ **Использование:**\n"
                "`.ff @username Текст сообщения`"
            )
            return

        target_raw, text = args[0], args[1]

        try:
            entity = await client.get_entity(target_raw)
            first = getattr(entity, "first_name", "") or ""
            last = getattr(entity, "last_name", "") or ""
            name = f"{first} {last}".strip() or getattr(entity, "username", str(entity.id))
            uid = entity.id

            await event.delete()
            await client.send_message(
                event.chat_id,
                f"[{name}](tg://user?id={uid}):\n{text}"
            )

        except Exception as e:
            await event.edit(f"❌ {e}")
