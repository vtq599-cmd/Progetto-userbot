from telethon import events
from telethon.tl.functions.messages import ExportChatInviteRequest

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}chatlink$", outgoing=True))
    async def chatlink_handler(event):
        if not (event.is_group or event.is_channel):
            await event.edit("❌ Используй в группе или канале")
            return

        try:
            chat = await event.get_chat()
            title = getattr(chat, "title", "Чат")
            username = getattr(chat, "username", None)

            if username:
                await event.edit(
                    f"🔗 **{title}**\n\n"
                    f"**Публичная ссылка:**\nhttps://t.me/{username}"
                )
                return

            try:
                result = await client(ExportInviteRequest(channel=event.chat_id))
            except Exception:
                result = await client(ExportChatInviteRequest(peer=event.chat_id))

            await event.edit(
                f"🔗 **{title}**\n\n"
                f"**Ссылка-приглашение:**\n{result.link}"
            )

        except Exception as e:
            await event.edit(f"❌ {e}")
