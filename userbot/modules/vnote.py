import os
import subprocess
import tempfile
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}vnote$", outgoing=True))
    async def vnote_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ Ответьте на видео")
            return

        is_video = reply.video or reply.gif or (
            reply.document and reply.document.mime_type
            and "video" in reply.document.mime_type
        )
        if not is_video:
            await event.edit("❌ Это не видео")
            return

        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except FileNotFoundError:
            await event.edit("❌ ffmpeg не установлен")
            return

        await event.edit("⭕️ **Конвертирую в кружочек...**")
        tmp_in = tmp_out = None
        try:
            tmp_in = tempfile.mktemp(suffix=".mp4")
            tmp_out = tempfile.mktemp(suffix=".mp4")
            await reply.download_media(tmp_in)

            subprocess.run([
                "ffmpeg", "-y",
                "-i", tmp_in,
                "-t", "60",
                "-vf", "crop=min(iw\\,ih):min(iw\\,ih),scale=384:384,fps=30",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-pix_fmt", "yuv420p",
                tmp_out,
            ], capture_output=True, check=True)

            await event.delete()
            await client.send_file(event.chat_id, tmp_out, video_note=True)

        except subprocess.CalledProcessError as e:
            await event.edit(f"❌ ffmpeg ошибка:\n`{e.stderr.decode()[-300:]}`")
        except Exception as e:
            await event.edit(f"❌ {e}")
        finally:
            for f in [tmp_in, tmp_out]:
                if f and os.path.exists(f):
                    os.remove(f)
