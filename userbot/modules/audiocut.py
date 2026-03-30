import os
import subprocess
import tempfile
from telethon import events

def parse_time(t):
    if ":" in t:
        parts = t.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    return int(t)

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}cut ?(.*)", outgoing=True))
    async def cut_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ Ответьте на аудио или голосовое сообщение")
            return

        is_audio = reply.audio or reply.voice or (
            reply.document and reply.document.mime_type
            and "audio" in reply.document.mime_type
        )
        if not is_audio:
            await event.edit("❌ Это не аудио/голосовое сообщение")
            return

        args = event.pattern_match.group(1).strip().split()
        if len(args) < 2:
            await event.edit("❌ Укажи начало и конец:\n`.cut 0:30 1:00`")
            return

        try:
            start = parse_time(args[0])
            end = parse_time(args[1])
        except Exception:
            await event.edit("❌ Неверный формат. Используй `м:сс` или секунды")
            return

        if start >= end:
            await event.edit("❌ Начало должно быть меньше конца")
            return

        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except FileNotFoundError:
            await event.edit("❌ ffmpeg не установлен")
            return

        await event.edit("✂️ **Вырезаю фрагмент...**")
        tmp_in = tmp_out = None
        try:
            tmp_in = tempfile.mktemp(suffix=".ogg")
            tmp_out = tempfile.mktemp(suffix=".ogg")
            await reply.download_media(tmp_in)

            subprocess.run([
                "ffmpeg", "-y",
                "-i", tmp_in,
                "-ss", str(start),
                "-t", str(end - start),
                "-c", "copy",
                tmp_out,
            ], capture_output=True, check=True)

            is_voice = bool(reply.voice)
            await event.delete()
            await client.send_file(
                event.chat_id,
                tmp_out,
                voice_note=is_voice,
                caption=f"✂️ **Фрагмент аудио**\n⏱ {args[0]} → {args[1]}"
            )
        except subprocess.CalledProcessError as e:
            await event.edit(f"❌ ffmpeg ошибка: `{e}`")
        except Exception as e:
            await event.edit(f"❌ {e}")
        finally:
            for f in [tmp_in, tmp_out]:
                if f and os.path.exists(f):
                    os.remove(f)
