import re

from telethon import events

from modules.history import first_cached


def _name(user):
    return (
        f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
        or str(getattr(user, "id", "неизвестно"))
    )


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}first(?:\s+(.+))?$", outgoing=True))
    async def first_handler(event):
        arg = (event.pattern_match.group(1) or "").strip()
        reply = await event.get_reply_message()
        sender_id = None
        if arg:
            try:
                sender_id = (await client.get_entity(arg)).id
            except Exception:
                return await event.edit("❌ Пользователь не найден.")
        elif reply:
            sender_id = reply.sender_id

        await event.edit("🔍 Ищу первое доступное сообщение...")
        try:
            first = None
            async for message in client.iter_messages(
                event.chat_id,
                from_user=sender_id,
                reverse=True,
            ):
                first = message
                break
            cached = first_cached(event.chat_id, sender_id)
            if first and (not cached or first.id <= cached["message_id"]):
                user = await first.get_sender()
                record = {
                    "message_id": first.id,
                    "date": first.date.strftime("%d.%m.%Y %H:%M"),
                    "text": first.text or "[медиа]",
                    "sender": _name(user),
                }
            elif cached:
                record = {
                    "message_id": cached["message_id"],
                    "date": cached["date"][:16].replace("T", " "),
                    "text": cached["text"],
                    "sender": str(cached["sender_id"]),
                }
            else:
                return await event.edit(
                    "❌ Сообщений не найдено. Удалённые до запуска бота сообщения Telegram не возвращает."
                )
            chat_id = str(event.chat_id)
            link = (
                f"https://t.me/c/{chat_id[4:]}/{record['message_id']}"
                if chat_id.startswith("-100")
                else "ссылка недоступна"
            )
            await event.edit(
                f"📜 **Первое доступное сообщение**\n"
                f"👤 {record['sender']}\n"
                f"📅 {record['date']}\n"
                f"💬 {record['text'][:300]}\n"
                f"🔗 {link}",
                parse_mode=None,
            )
        except Exception as exc:
            await event.edit(f"❌ First: {exc}")