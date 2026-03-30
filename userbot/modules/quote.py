import aiohttp
import base64
import io
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}q$", outgoing=True))
    async def q_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ Ответьте на сообщение командой `.q`")
            return

        await event.edit("✍️ **Создаю цитату...**")
        try:
            sender = await reply.get_sender()
            first = getattr(sender, "first_name", "") or ""
            last = getattr(sender, "last_name", "") or ""
            name = f"{first} {last}".strip() or str(sender.id)

            avatar_b64 = None
            try:
                photos = await client.get_profile_photos(sender.id, limit=1)
                if photos:
                    buf = io.BytesIO()
                    await client.download_media(photos[0], buf)
                    buf.seek(0)
                    avatar_b64 = base64.b64encode(buf.read()).decode()
            except Exception:
                pass

            text = reply.text or reply.caption or "[медиа]"

            payload = {
                "type": "quote",
                "format": "webp",
                "backgroundColor": "#1b1429",
                "width": 512,
                "height": 512,
                "scale": 2,
                "messages": [{
                    "entities": [],
                    "media": {"mediaType": ""},
                    "avatar": True,
                    "from": {
                        "id": sender.id,
                        "name": name,
                        "photo": {
                            "url": f"data:image/jpeg;base64,{avatar_b64}" if avatar_b64 else ""
                        },
                        "type": "private",
                    },
                    "text": text,
                    "replyMessage": {},
                }],
            }

            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://bot.lyo.su/quote/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as r:
                    if r.status != 200:
                        raise Exception(f"HTTP {r.status}")
                    data = await r.json()

            img_b64 = data.get("result", {}).get("image")
            if not img_b64:
                raise Exception("API не вернул изображение")

            file = io.BytesIO(base64.b64decode(img_b64))
            file.name = "quote.webp"

            await event.delete()
            await client.send_file(event.chat_id, file)

        except Exception as e:
            await event.edit(f"❌ {e}")
