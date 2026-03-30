import os
import tempfile
from gtts import gTTS
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}tts ?(\w{{2}})? ?([\s\S]*)", outgoing=True))
    async def tts_handler(event):
        lang = event.pattern_match.group(1) or "ru"
        text = event.pattern_match.group(2).strip()
        reply = await event.get_reply_message()
        if not text and reply:
            text = reply.text or ""
        if not text:
            await event.edit("❗ Укажите текст.")
            return
        await event.edit("🎙 Генерирую...")
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name
            gTTS(text=text, lang=lang).save(tmp)
            await event.delete()
            await client.send_file(event.chat_id, tmp, voice_note=True)
            os.unlink(tmp)
        except Exception as e:
            await event.edit(f"❌ {e}")
