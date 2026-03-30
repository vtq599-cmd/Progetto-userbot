from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}purge$", outgoing=True))
    async def purge_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❗ Ответьте на сообщение.")
            return
        await event.delete()
        ids = []
        async for msg in client.iter_messages(event.chat_id, min_id=reply.id - 1, max_id=event.id + 1):
            ids.append(msg.id)
        if ids:
            await client.delete_messages(event.chat_id, ids)

    @client.on(events.NewMessage(pattern=rf"\{prefix}purgeme ?(\d*)", outgoing=True))
    async def purgeme_handler(event):
        count = int(event.pattern_match.group(1) or 10)
        me = await client.get_me()
        ids = []
        async for msg in client.iter_messages(event.chat_id, from_user=me.id, limit=count + 1):
            ids.append(msg.id)
        if ids:
            await client.delete_messages(event.chat_id, ids)
