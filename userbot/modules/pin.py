from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}pin$", outgoing=True))
    async def pin_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❗ Ответьте на сообщение.")
            return
        await client.pin_message(event.chat_id, reply.id, notify=False)
        await event.edit("📌 Закреплено.")

    @client.on(events.NewMessage(pattern=rf"\{prefix}unpin$", outgoing=True))
    async def unpin_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❗ Ответьте на сообщение.")
            return
        await client.unpin_message(event.chat_id, reply.id)
        await event.edit("🔓 Откреплено.")

    @client.on(events.NewMessage(pattern=rf"\{prefix}unpinall$", outgoing=True))
    async def unpinall_handler(event):
        await client.unpin_message(event.chat_id)
        await event.edit("🔓 Все откреплены.")
