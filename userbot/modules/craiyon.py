import aiohttp
import base64
import io
import asyncio
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}craiyon ?([\s\S]*)", outgoing=True))
    async def craiyon_handler(event):
        prompt = event.pattern_match.group(1).strip()
        if not prompt:
            await event.edit("❌ Укажи запрос\nПример: `.craiyon cute cat`")
            return

        await event.edit("🎨 **Генерирую изображения...**\n⏳ Подожди ~30-60 секунд")

        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://api.craiyon.com/v3",
                    json={
                        "prompt": prompt,
                        "negative_prompt": "",
                        "model": "art",
                        "token": None,
                        "version": "35s5hfwn9n78gb06",
                    },
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as r:
                    data = await r.json()

            images = data.get("images", [])
            if not images:
                return await event.edit("❌ Изображения не сгенерированы")

            files = []
            for i, img_b64 in enumerate(images[:4]):
                buf = io.BytesIO(base64.b64decode(img_b64))
                buf.name = f"craiyon_{i+1}.jpg"
                files.append(buf)

            await event.delete()
            await client.send_file(
                event.chat_id,
                files,
                caption=f"🎨 **Craiyon:** {prompt}"
            )

        except asyncio.TimeoutError:
            await event.edit("❌ Таймаут — сервер не ответил, попробуй ещё раз")
        except Exception as e:
            await event.edit(f"❌ {e}")
