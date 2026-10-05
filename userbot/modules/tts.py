import os
import re
import tempfile

from telethon import events


VOICES = {
    "ru": "ru-RU-SvetlanaNeural",
    "ru_female": "ru-RU-SvetlanaNeural",
    "ru_male": "ru-RU-DmitryNeural",
    "en": "en-US-JennyNeural",
    "en_male": "en-US-GuyNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
}


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}tts(?:\s+(\S+))?\s*([\s\S]*)$", outgoing=True))
    async def tts_handler(event):
        voice_key = (event.pattern_match.group(1) or "ru").lower()
        text = (event.pattern_match.group(2) or "").strip()
        if voice_key not in VOICES and "-" not in voice_key:
            text = f"{voice_key} {text}".strip()
            voice_key = "ru"
        reply = await event.get_reply_message()
        if not text and reply:
            text = reply.text or ""
        if not text:
            return await event.edit("❗ Укажи текст или ответь на сообщение.")

        voice = VOICES.get(voice_key, voice_key if "-" in voice_key else VOICES["ru"])
        await event.edit("🎙 Генерирую голосовое...")
        tmp = tempfile.mktemp(suffix=".mp3")
        try:
            try:
                import edge_tts

                await edge_tts.Communicate(text, voice).save(tmp)
            except ImportError:
                from gtts import gTTS

                gTTS(text=text, lang=voice[:2]).save(tmp)
            await event.delete()
            await client.send_file(event.chat_id, tmp, voice_note=True)
        except Exception as exc:
            await event.edit(f"❌ TTS: {exc}")
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)