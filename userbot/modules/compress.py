import io
import os
import tempfile
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}compress ?(\d*)", outgoing=True))
    async def compress_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ Ответьте на фотографию")
            return

        is_photo = reply.photo or (
            reply.document and reply.document.mime_type
            and reply.document.mime_type.startswith("image/")
        )
        if not is_photo:
            await event.edit("❌ Это не фотография")
            return

        arg = event.pattern_match.group(1).strip()
        quality = max(1, min(95, int(arg))) if arg.isdigit() else 75

        await event.edit("🗜 **Сжимаю изображение...**")
        tmp_in = None
        try:
            from PIL import Image

            tmp_in = tempfile.mktemp(suffix=".jpg")
            await reply.download_media(tmp_in)
            orig_size = os.path.getsize(tmp_in)

            img = Image.open(tmp_in)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            buf.seek(0)
            new_size = len(buf.getvalue())
            saved = orig_size - new_size
            saved_pct = round(saved / orig_size * 100) if orig_size else 0

            buf.seek(0)
            buf.name = "compressed.jpg"

            await event.delete()
            await client.send_file(
                event.chat_id,
                buf,
                caption=(
                    f"🗜 **Сжато!**\n"
                    f"📦 До: **{orig_size // 1024} КБ**\n"
                    f"📦 После: **{new_size // 1024} КБ**\n"
                    f"💾 Сэкономлено: **{saved // 1024} КБ ({saved_pct}%)**\n"
                    f"🎚 Качество: **{quality}%**"
                ),
            )
        except ImportError:
            await event.edit("❌ Pillow не установлен: `pip install Pillow`")
        except Exception as e:
            await event.edit(f"❌ {e}")
        finally:
            if tmp_in and os.path.exists(tmp_in):
                os.remove(tmp_in)
