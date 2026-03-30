import os
import tempfile
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}save$", outgoing=True))
    async def save_media_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.edit("❗ Ответьте на медиафайл.")
            return
        await event.edit("💾 Сохраняю...")
        try:
            tmp = await client.download_media(reply, file=tempfile.mkdtemp() + "/")
            await client.send_file("me", tmp, caption="💾 Сохранено юзерботом")
            os.remove(tmp)
            await event.edit("✅ Отправлено в **Избранное**!")
        except Exception as e:
            await event.edit(f"❌ {e}")
