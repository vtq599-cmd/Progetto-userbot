import re

from telethon import events

from modules.history import get_deleted


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}restore(?:\s+(\d+))?$", outgoing=True))
    async def restore_handler(event):
        count = min(int(event.pattern_match.group(1) or 1), 10)
        deleted = get_deleted(event.chat_id, count)
        await event.delete()
        if not deleted:
            return
        for record in deleted:
            text = record["text"]
            await client.send_message(
                event.chat_id,
                f"♻️ **Восстановлено из кэша**\n{text}",
            )