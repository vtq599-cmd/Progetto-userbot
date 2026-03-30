from telethon import events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}creact ?(.*)", outgoing=True))
    async def creact_handler(event):
        emoji = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()

        if not reply:
            await event.edit("❌ Ответьте на сообщение")
            return
        if not emoji:
            await event.edit("❌ Укажи эмодзи: `.creact ❤️`")
            return

        try:
            channels = []
            async for dialog in client.iter_dialogs():
                if dialog.is_channel:
                    ch = dialog.entity
                    if getattr(ch, "creator", False) or getattr(ch, "admin_rights", None):
                        channels.append(ch)

            if not channels:
                await event.edit("❌ У тебя нет каналов с правами администратора")
                return

            channel = channels[0]
            await client(SendReactionRequest(
                peer=reply.peer_id,
                msg_id=reply.id,
                reaction=[ReactionEmoji(emoticon=emoji)],
                send_as=channel,
            ))

            ch_name = getattr(channel, "title", str(channel.id))
            await event.edit(f"✅ Реакция {emoji} поставлена от имени **{ch_name}**")

        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}creactlist$", outgoing=True))
    async def creactlist_handler(event):
        await event.edit("📋 **Получаю список каналов...**")
        try:
            channels = []
            async for dialog in client.iter_dialogs():
                if dialog.is_channel:
                    ch = dialog.entity
                    if getattr(ch, "creator", False) or getattr(ch, "admin_rights", None):
                        channels.append(ch)

            if not channels:
                await event.edit("❌ Нет доступных каналов")
                return

            lines = ["📢 **Твои каналы:**\n"]
            for ch in channels:
                username = f"@{ch.username}" if getattr(ch, "username", None) else ""
                lines.append(f"• **{ch.title}** {username}")

            await event.edit("\n".join(lines))
        except Exception as e:
            await event.edit(f"❌ {e}")
