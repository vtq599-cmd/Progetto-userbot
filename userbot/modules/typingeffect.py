import asyncio
from telethon import events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}type (\d*) ?([\s\S]+)", outgoing=True))
    async def typing_handler(event):
        delay_str = event.pattern_match.group(1).strip()
        text = event.pattern_match.group(2).strip()
        delay = int(delay_str) if delay_str else 2
        await event.delete()
        await client(SetTypingRequest(peer=event.chat_id, action=SendMessageTypingAction()))
        await asyncio.sleep(delay)
        await client.send_message(event.chat_id, text)
