import aiohttp
import os
import tempfile
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}tt ?(.*)", outgoing=True))
    async def tt_handler(event):
        url = event.pattern_match.group(1).strip()
        if not url:
            await event.edit("❌ Укажи ссылку на TikTok видео\nПример: `.tt https://vm.tiktok.com/xxx`")
            return

        await event.edit("⏳ Скачиваю видео...")
        tmp_path = None
        try:
            params = {"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1}
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

            async with aiohttp.ClientSession(headers=headers) as s:
                async with s.post("https://www.tikwm.com/api/", data=params) as r:
                    data = await r.json()

            if data.get("code") != 0:
                return await event.edit(f"❌ Ошибка API: {data.get('msg', 'Неизвестная ошибка')}")

            info = data["data"]
            video_url = info.get("hdplay") or info.get("play") or info.get("wmplay")
            if not video_url:
                return await event.edit("❌ Не удалось найти ссылку на видео")
            if video_url.startswith("/"):
                video_url = "https://www.tikwm.com" + video_url

            author = info.get("author", {}).get("unique_id", "tiktok")
            title = info.get("title", "")[:50]
            tmp_path = tempfile.mktemp(suffix=".mp4")

            async with aiohttp.ClientSession(headers=headers) as s:
                async with s.get(video_url) as r:
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
                event.chat_id, tmp_path,
                caption=f"🎵 **{title}**\n👤 @{author}",
                supports_streaming=True
            )
        except Exception as e:
            await event.edit(f"❌ {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
