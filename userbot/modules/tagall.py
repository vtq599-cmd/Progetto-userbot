import asyncio
from telethon import events
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.functions.channels import GetParticipantsRequest

_running = False

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}tagall ?([\s\S]*)", outgoing=True))
    async def tagall_handler(event):
        global _running
        if not (event.is_group or event.is_channel):
            await event.edit("❌ Используй только в группах")
            return

        args = event.pattern_match.group(1).strip()
        _running = True
        await event.edit("👥 **Тегаю участников...**")

        try:
            all_participants = []
            offset = 0
            limit = 100

            while True:
                participants = await client(GetParticipantsRequest(
                    channel=event.chat_id,
                    filter=ChannelParticipantsSearch(""),
                    offset=offset,
                    limit=limit,
                    hash=0,
                ))
                if not participants.users:
                    break
                all_participants.extend(participants.users)
                offset += len(participants.users)
                if len(participants.users) < limit:
                    break

            users = [u for u in all_participants if not u.bot]
            header = f"{args}\n" if args else ""
            tagged = 0

            await event.delete()
            for i in range(0, len(users), 5):
                if not _running:
                    await client.send_message(event.chat_id, "🛑 **Тег остановлен**")
                    return
                chunk = users[i:i + 5]
                mentions = " ".join(
                    f"[{u.first_name or str(u.id)}](tg://user?id={u.id})"
                    for u in chunk
                )
                await client.send_message(event.chat_id, f"{header}{mentions}")
                tagged += len(chunk)
                await asyncio.sleep(1.5)

            await client.send_message(event.chat_id, f"✅ **Отмечено участников: {tagged}**")

        except Exception as e:
            await client.send_message(event.chat_id, f"❌ {e}")
        finally:
            _running = False

    @client.on(events.NewMessage(pattern=rf"\{prefix}untagall$", outgoing=True))
    async def untagall_handler(event):
        global _running
        _running = False
        await event.edit("🛑 **Тег остановлен**")
