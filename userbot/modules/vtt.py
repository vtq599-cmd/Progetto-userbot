import aiohttp
import os
import tempfile
from telethon import events

WIT_TOKEN = "JVDPWQIW6XHWJBNBDWB5EVLLFHCQKBQX"

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}vtt$", outgoing=True))
    async def vtt_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ Ответьте на голосовое сообщение")
            return

        is_voice = (
            reply.voice
            or reply.audio
            or (reply.document and reply.document.mime_type and "audio" in reply.document.mime_type)
        )
        if not is_voice:
            await event.edit("❌ Это не голосовое/аудио сообщение")
            return

        await event.edit("🎙️ **Расшифровываю...**")
        tmp_path = None
        try:
            tmp_path = tempfile.mktemp(suffix=".ogg")
            await reply.download_media(tmp_path)

            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            mime = "audio/ogg"
            if reply.audio and reply.audio.mime_type:
                mime = reply.audio.mime_type
            elif reply.document and reply.document.mime_type:
                mime = reply.document.mime_type

            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://api.wit.ai/speech?v=20220622",
                    headers={
                        "Authorization": f"Bearer {WIT_TOKEN}",
                        "Content-Type": mime,
                    },
                    data=audio_bytes,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as r:
                    data = await r.json()

            text = (data.get("text") or "").strip()
            if not text:
                return await event.edit("🤷 Не удалось распознать речь")

            sender = reply.sender
            name = ""
            if sender:
                name = f"{getattr(sender, 'first_name', '') or ''} {getattr(sender, 'last_name', '') or ''}".strip()

            await event.edit(
                f"🎙️ **Расшифровка{' от ' + name if name else ''}:**\n\n{text}"
            )

        except Exception as e:
            await event.edit(f"❌ {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
