import asyncio
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}gp ?(.*)", outgoing=True))
    async def ghostping_handler(event):
        mention = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        await event.delete()
        if mention:
            msg = await client.send_message(event.chat_id, mention)
        elif reply:
            user = reply.sender
            if not user:
                return
            msg = await client.send_message(event.chat_id, f"[{user.first_name}](tg://user?id={user.id})")
        else:
            return
        await asyncio.sleep(0.5)
        await msg.delete()
