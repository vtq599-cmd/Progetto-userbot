import os
import re
import tempfile

from telethon import events


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}save$", outgoing=True))
    async def save_media(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.delete()
        tmp_dir = tempfile.mkdtemp()
        try:
            tmp = await client.download_media(reply, file=tmp_dir)
            await event.delete()
            await client.send_file("me", tmp)
        except Exception:
            await event.delete()
        finally:
            if tmp_dir and os.path.isdir(tmp_dir):
                for name in os.listdir(tmp_dir):
                    os.unlink(os.path.join(tmp_dir, name))
                os.rmdir(tmp_dir)