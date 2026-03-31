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

            # Исправлено: правильный метод скачивания аватара
            avatar_b64 = None
            try:
                buf = io.BytesIO()
                await client.download_profile_photo(sender.id, file=buf)
                buf.seek(0)
                raw = buf.read()
                if raw:
                    avatar_b64 = base64.b64encode(raw).decode()
            except Exception:
                pass

            text = reply.text or reply.caption or "[медиа]"

            payload = {
                "type": "quote",
                "format": "webp",
                "backgroundColor": "#1b1429",
                "width": 512,
                "scale": 2,
                "messages": [{
                    "entities": [],
                    "avatar": True,
                    "from": {
                        "id": sender.id,
                        "name": name,
                        "photo": {
                            "url": f"data:image/jpeg;base64,{avatar_b64}" if avatar_b64 else ""
                        },
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
                        body = await r.text()
                        raise Exception(f"HTTP {r.status}: {body[:300]}")
                    data = await r.json()

            # Исправлено: API может вернуть в разных форматах
            img_b64 = (
                data.get("result", {}).get("image")
                or data.get("image")
            )
            if not img_b64:
                raise Exception(f"Нет изображения в ответе: {str(data)[:200]}")

            file = io.BytesIO(base64.b64decode(img_b64))
            file.name = "quote.webp"

            await event.delete()
            await client.send_file(event.chat_id, file)

        except Exception as e:
            await event.edit(f"❌ {e}")