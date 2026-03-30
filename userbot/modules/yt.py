import aiohttp
import os
import tempfile
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}yt ?(.*)", outgoing=True))
    async def yt_handler(event):
        url = event.pattern_match.group(1).strip()
        if not url:
            await event.edit("❌ Укажи ссылку\nПример: `.yt https://youtu.be/xxx`")
            return

        await event.edit("⏳ **Скачиваю видео с YouTube...**")

        tmp_path = None
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://api.cobalt.tools/api/json",
                    json={
                        "url": url,
                        "vQuality": "720",
                        "filenamePattern": "basic",
                        "isAudioOnly": False,
                        "disableMetadata": True,
                    },
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as r:
                    if r.status != 200:
                        raise Exception(f"HTTP {r.status}")
                    data = await r.json()

            status = data.get("status")
            if status == "error":
                raise Exception(data.get("text", "Неизвестная ошибка"))
            elif status in ("redirect", "stream"):
                video_url = data.get("url")
            elif status == "picker":
                video_url = data["picker"][0]["url"]
            else:
                raise Exception(f"Неожиданный статус: {status}")

            if not video_url:
                raise Exception("Не удалось получить ссылку на видео")

            tmp_path = tempfile.mktemp(suffix=".mp4")
            async with aiohttp.ClientSession() as s:
                async with s.get(video_url, timeout=aiohttp.ClientTimeout(total=300)) as r:
                    with open(tmp_path, "wb") as f:
                        while True:
                            chunk = await r.content.read(65536)
                            if not chunk:
                                break
                            f.write(chunk)

            if os.path.getsize(tmp_path) > 50 * 1024 * 1024:
                return await event.edit(f"❌ Файл слишком большой\n🔗 [Прямая ссылка]({video_url})")

            await event.delete()
            await client.send_file(
                event.chat_id,
                tmp_path,
                caption=f"🎬 **YouTube**\n🔗 {url}",
                supports_streaming=True
            )

        except Exception as e:
            await event.edit(f"❌ {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
