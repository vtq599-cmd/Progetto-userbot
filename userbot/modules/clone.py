import io
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

_backup = None

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}clone ?(.*)", outgoing=True))
    async def clone_handler(event):
        global _backup
        arg = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()

        if not arg and not reply:
            await event.edit("❌ Укажи @username или ответь на сообщение")
            return

        await event.edit("🎭 **Клонирую профиль...**")
        try:
            target = await reply.get_sender() if reply else await client.get_entity(arg)

            me = await client.get_me()
            _backup = {
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
            }

            target_first = getattr(target, "first_name", "") or ""
            target_last = getattr(target, "last_name", "") or ""

            await client(UpdateProfileRequest(
                first_name=target_first,
                last_name=target_last,
            ))

            try:
                photos = await client.get_profile_photos(target.id, limit=1)
                if photos:
                    buf = io.BytesIO()
                    await client.download_media(photos[0], buf)
                    buf.seek(0)
                    uploaded = await client.upload_file(buf)
                    await client(UploadProfilePhotoRequest(file=uploaded))
            except Exception:
                pass

            target_name = f"{target_first} {target_last}".strip()
            await event.edit(
                f"🎭 **Теперь ты:** {target_name}\n\n"
                f"↩️ Восстановить профиль: `.unclone`"
            )
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}unclone$", outgoing=True))
    async def unclone_handler(event):
        global _backup
        if not _backup:
            await event.edit("❌ Нет сохранённого профиля для восстановления")
            return
        try:
            await client(UpdateProfileRequest(
                first_name=_backup.get("first_name", ""),
                last_name=_backup.get("last_name", ""),
            ))
            _backup = None
            await event.edit("✅ **Профиль восстановлен!**")
        except Exception as e:
            await event.edit(f"❌ {e}")
