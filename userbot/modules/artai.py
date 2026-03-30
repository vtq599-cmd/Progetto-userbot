import aiohttp
import io
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}artai ?([\s\S]*)", outgoing=True))
    async def artai_handler(event):
        prompt = event.pattern_match.group(1).strip()
        if not prompt:
            await event.edit("❌ Укажи запрос\nПример: `.artai sunset over ocean`")
            return

        await event.edit("🎨 **Генерирую изображение...**")

        try:
            prompt_encoded = prompt.replace(" ", "%20")
            url = (
                f"https://image.pollinations.ai/prompt/{prompt_encoded}"
                f"?width=1024&height=1024&nologo=true&enhance=true"
            )

            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=60)) as r:
                    if r.status != 200:
                        raise Exception(f"HTTP {r.status}")
                    img_bytes = await r.read()

            file = io.BytesIO(img_bytes)
            file.name = "artai.jpg"

            await event.delete()
            await client.send_file(
                event.chat_id,
                file,
                caption=f"🎨 **ArtAI:** {prompt}"
            )

        except Exception as e:
            await event.edit(f"❌ {e}")
