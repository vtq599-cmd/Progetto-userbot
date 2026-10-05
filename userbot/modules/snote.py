import asyncio
import re

from telethon import events


_secret_messages = {}


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}snote(?:\s+([\s\S]*))?$", outgoing=True))
    async def snote_handler(event):
        text = (event.pattern_match.group(1) or "").strip()
        if not text:
            return await event.edit("❌ Укажи текст: `.snote секретное сообщение`")

        await event.delete()
        secret = await client.send_message(event.chat_id, text)
        _secret_messages[(event.chat_id, secret.id)] = True

        async def fallback_delete():
            await asyncio.sleep(300)
            if _secret_messages.pop((event.chat_id, secret.id), None):
                try:
                    await secret.delete()
                except Exception:
                    pass

        asyncio.create_task(fallback_delete())

    @client.on(events.MessageRead())
    async def delete_after_read(event):
        if not event.outbox or event.chat_id is None or event.max_id is None:
            return
        for key in list(_secret_messages):
            chat_id, message_id = key
            if chat_id == event.chat_id and event.is_read(message_id):
                _secret_messages.pop(key, None)
                try:
                    await client.delete_messages(chat_id, message_id)
                except Exception:
                    pass