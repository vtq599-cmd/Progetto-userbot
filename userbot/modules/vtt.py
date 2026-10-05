import os
import re
import tempfile

import aiohttp
from telethon import events


WIT_TOKEN = os.environ.get("WIT_TOKEN", "").strip()


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}vtt$", outgoing=True))
    async def vtt_handler(event):
        reply = await event.get_reply_message()
        mime = getattr(getattr(reply, "file", None), "mime_type", None)
        if not reply or not (
            reply.voice
            or reply.audio
            or (reply.document and mime and mime.startswith("audio/"))
        ):
            return await event.edit("❌ Ответь на голосовое или аудиофайл.")
        if not WIT_TOKEN:
            return await event.edit("❌ Для `.vtt` добавь WIT_TOKEN в userbot/.env.")

        await event.edit("🎙️ Расшифровываю...")
        tmp = tempfile.mktemp(suffix=".ogg")
        try:
            await reply.download_media(tmp)
            with open(tmp, "rb") as audio:
                payload = audio.read()
            mime = mime or "audio/ogg"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.wit.ai/speech?v=20220622",
                    headers={
                        "Authorization": f"Bearer {WIT_TOKEN}",
                        "Content-Type": mime,
                    },
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=90),
                ) as response:
                    data = await response.json(content_type=None)
                    if response.status != 200:
                        raise RuntimeError(data.get("error", f"HTTP {response.status}"))
            text = (data.get("text") or "").strip()
            await event.edit(f"🎙️ **Расшифровка:**\n\n{text}" if text else "🤷 Речь не распознана.")
        except Exception as exc:
            await event.edit(f"❌ VTT: {exc}")
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)