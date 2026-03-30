from telethon import events
from telethon.tl.functions.messages import GetCommonChatsRequest

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}ui ?(.*)", outgoing=True))
    async def ui_handler(event):
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
            name = f"{first} {last}".strip() or "—"
            username = f"@{user.username}" if getattr(user, "username", None) else "—"
            phone = getattr(user, "phone", None) or "—"

            try:
                common = await client(GetCommonChatsRequest(user_id=user.id, max_id=0, limit=100))
                common_count = len(common.chats)
            except Exception:
                common_count = "—"

            status = user.status
            status_str = "—"
            if status:
                stype = type(status).__name__
                if stype == "UserStatusOnline":
                    status_str = "🟢 Онлайн сейчас"
                elif stype == "UserStatusRecently":
                    status_str = "🟡 Был(а) недавно"
                elif stype == "UserStatusLastWeek":
                    status_str = "🟠 На этой неделе"
                elif stype == "UserStatusLastMonth":
                    status_str = "🔴 В этом месяце"
                elif stype == "UserStatusOffline":
                    dt = getattr(status, "was_online", None)
                    status_str = f"⚫️ {dt.strftime('%d.%m.%Y %H:%M')}" if dt else "⚫️ Оффлайн"
                elif stype == "UserStatusEmpty":
                    status_str = "❓ Скрыт"

            badges = []
            if getattr(user, "bot", False):      badges.append("🤖 Бот")
            if getattr(user, "premium", False):  badges.append("⭐️ Premium")
            if getattr(user, "verified", False): badges.append("✅ Верифицирован")
            if getattr(user, "scam", False):     badges.append("⚠️ Скам")
            if getattr(user, "fake", False):     badges.append("🚫 Фейк")

            text = (
                f"👤 **Информация о пользователе**\n\n"
                f"🏷 **Имя:** {name}\n"
                f"🔗 **Username:** {username}\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"📱 **Телефон:** {phone}\n"
                f"🕐 **Статус:** {status_str}\n"
                f"💬 **Общих чатов:** {common_count}\n"
            )
            if badges:
                text += f"🎖 **Метки:** {' | '.join(badges)}\n"
            text += f"\n🔗 [Открыть профиль](tg://user?id={user.id})"

            await event.edit(text)
        except Exception as e:
            await event.edit(f"❌ {e}")
