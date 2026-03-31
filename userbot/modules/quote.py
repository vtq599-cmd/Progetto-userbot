from telethon import events
import asyncio

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}q$", outgoing=True))
    async def q_handler(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("❌ Ответьте на сообщение командой")
            return

        await event.edit("✍️ Создаю цитату...")
        try:
            quotly = await client.get_entity("QuotLyBot")

            # Пересылаем сообщение боту
            forwarded = await client.forward_messages(quotly, reply)
            fwd_id = forwarded[0].id if isinstance(forwarded, list) else forwarded.id

            # Ждём ответ до 30 секунд
            sticker = None
            for _ in range(15):
                await asyncio.sleep(2)
                msgs = await client.get_messages(quotly, limit=5)
                for msg in msgs:
                    if msg.id > fwd_id and msg.sticker:
                        sticker = msg
                        break
                if sticker:
                    break

            if not sticker:
                raise Exception("QuotLyBot не ответил за 30 секунд")

            await event.delete()
            await client.send_file(event.chat_id, sticker.media)

            # Чистим переписку с ботом
            try:
                await client.delete_messages(quotly, [fwd_id, sticker.id])
            except Exception:
                pass

        except Exception as e:
            await event.edit(f"❌ {type(e).__name__}: {e or '(пусто)'}")