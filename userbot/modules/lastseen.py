from datetime import datetime, timezone
from telethon import events

def format_delta(dt):
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    seconds = int((now - dt).total_seconds())
    if seconds < 60:        return f"{seconds} сек. назад"
    elif seconds < 3600:    return f"{seconds // 60} мин. назад"
    elif seconds < 86400:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h} ч. {m} мин. назад"
    elif seconds < 2592000: return f"{seconds // 86400} дн. назад"
    else:                   return f"{seconds // 2592000} мес. назад"

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}ls ?(.*)", outgoing=True))
    async def ls_handler(event):
        arg = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()

        await event.edit("🔍 **Получаю информацию...**")
        try:
            if reply:
                user = await reply.get_sender()
            elif arg:
                user = await client.get_entity(arg)
            else:
                await event.edit("❌ Укажи @username или ответь на сообщение")
                return

            first = getattr(user, "first_name", "") or ""
            last = getattr(user, "last_name", "") or ""
            name = f"{first} {last}".strip() or str(user.id)
            username = f"@{user.username}" if getattr(user, "username", None) else ""

            status = getattr(user, "status", None)
            stype = type(status).__name__ if status else "Unknown"

            if stype == "UserStatusOnline":
                result = "🟢 **Онлайн прямо сейчас!**"
            elif stype == "UserStatusOffline":
                was_online = getattr(status, "was_online", None)
                if was_online:
                    result = (
                        f"⚫️ **Последний раз онлайн:**\n"
                        f"📅 {was_online.strftime('%d.%m.%Y в %H:%M')}\n"
                        f"⏰ {format_delta(was_online)}"
                    )
                else:
                    result = "⚫️ **Оффлайн** (точное время скрыто)"
            elif stype == "UserStatusRecently":
                result = "🟡 **Был(а) в сети недавно**\n_(менее 2-3 дней назад)_"
            elif stype == "UserStatusLastWeek":
                result = "🟠 **Был(а) в сети на этой неделе**\n_(от 3 до 7 дней назад)_"
            elif stype == "UserStatusLastMonth":
                result = "🔴 **Был(а) в сети в этом месяце**\n_(от 7 до 30 дней назад)_"
            else:
                result = "❓ **Статус скрыт пользователем**"

            await event.edit(f"👤 **{name}** {username}\n\n{result}")

        except Exception as e:
            await event.edit(f"❌ {e}")
