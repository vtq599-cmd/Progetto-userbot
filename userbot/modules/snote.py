import asyncio
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}snote ?([\s\S]*)", outgoing=True))
    async def snote_handler(event):
        text = event.pattern_match.group(1).strip()
        if not text:
            await event.edit("❌ Укажи текст: `.snote Это секретное сообщение`")
            return

        await event.delete()

        msg = await client.send_message(
            event.chat_id,
            f"🔐 **Секретное сообщение**\n\n"
            f"{text}\n\n"
            f"_⏳ Удалится через 30 секунд_"
        )

        for i in range(25, 0, -5):
            await asyncio.sleep(5)
            try:
                await msg.edit(
                    f"🔐 **Секретное сообщение**\n\n"
                    f"{text}\n\n"
                    f"_⏳ Удалится через {i} сек_"
                )
            except Exception:
                break

        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
