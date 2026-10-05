import re

from telethon import events


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}d$", outgoing=True))
    async def delete_command(event):
        await event.delete()