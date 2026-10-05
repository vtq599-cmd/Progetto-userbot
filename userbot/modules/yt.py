import asyncio
import glob
import os
import re
import sys
import tempfile

from telethon import events


async def download_video(url, output_template):
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--format",
        "bestvideo*+bestaudio/best",
        "--merge-output-format",
        "mp4",
        "--output",
        output_template,
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=900)
    except asyncio.TimeoutError as exc:
        process.kill()
        await process.wait()
        raise RuntimeError("Таймаут скачивания (15 минут)") from exc
    if process.returncode:
        error = (stderr or stdout).decode(errors="replace")[-600:]
        raise RuntimeError(error or f"yt-dlp завершился с кодом {process.returncode}")


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}yt(?:\s+(.+))$", outgoing=True))
    async def yt_handler(event):
        url = event.pattern_match.group(1).strip()
        await event.edit("⏳ Скачиваю видео в максимальном доступном качестве...")
        tmp_dir = tempfile.mkdtemp()
        output_template = os.path.join(tmp_dir, "video.%(ext)s")
        try:
            await download_video(url, output_template)
            candidates = glob.glob(os.path.join(tmp_dir, "video.*"))
            if not candidates:
                raise RuntimeError("yt-dlp не создал видеофайл")
            tmp = next(
                (filename for filename in candidates if filename.endswith(".mp4")),
                candidates[0],
            )
            if os.path.getsize(tmp) > 2 * 1024 * 1024 * 1024:
                raise RuntimeError("Видео больше лимита Telegram в 2 ГБ")
            await event.delete()
            await client.send_file(event.chat_id, tmp, supports_streaming=True)
        except FileNotFoundError:
            await event.edit("❌ Не найден yt-dlp. Повтори установку Termux-зависимостей.")
        except Exception as exc:
            await event.edit(f"❌ YouTube: {exc}")
        finally:
            for filename in glob.glob(os.path.join(tmp_dir, "*")):
                os.unlink(filename)
            os.rmdir(tmp_dir)