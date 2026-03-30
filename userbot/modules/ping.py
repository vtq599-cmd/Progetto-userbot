import time
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}ping$", outgoing=True))
    async def ping_handler(event):
        start = time.time()
        msg = await event.edit("🏓 Pong!")
        elapsed = round((time.time() - start) * 1000, 2)
        await msg.edit(f"🏓 Pong! `{elapsed}ms`")
