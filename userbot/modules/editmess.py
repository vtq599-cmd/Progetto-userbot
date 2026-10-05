import re

from telethon import events

from modules.history import get_versions


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}editmess$", outgoing=True))
    async def edit_history(event):
        reply = await event.get_reply_message()
        if not reply:
            return await event.edit("Ответь на отредактированное сообщение.")
        versions = get_versions(event.chat_id, reply.id)
        if len(versions) < 2:
            return await event.edit("История этого сообщения ещё не накоплена.")

        lines = ["📝 **История изменений**"]
        for index, version in enumerate(versions, start=1):
            text = version["text"][:1000]
            lines.append(f"\n**Версия {index}:**\n{text}")
        await event.edit("\n".join(lines), parse_mode=None)