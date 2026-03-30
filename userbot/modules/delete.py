from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}(delete|del|d)$", outgoing=True))
    async def delete_handler(event):
        reply = await event.get_reply_message()
        if reply:
            await reply.delete()
        await event.delete()
