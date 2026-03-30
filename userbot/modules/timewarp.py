from datetime import datetime, timezone
from telethon import events

_cache = {}

def register(client, prefix):
    @client.on(events.NewMessage(incoming=True))
    async def tw_watcher(event):
        try:
            sender = await event.get_sender()
            if not sender or getattr(sender, "bot", False):
                return
            uid = str(sender.id)
            first = getattr(sender, "first_name", "") or ""
            last = getattr(sender, "last_name", "") or ""
            username = getattr(sender, "username", "") or ""
            name = f"{first} {last}".strip()

            history = _cache.get(uid, [])
            last_entry = history[-1] if history else {}
            if last_entry.get("name") != name or last_entry.get("username") != username:
                history.append({
                    "name": name,
                    "username": username,
                    "date": datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M"),
                })
                _cache[uid] = history[-20:]
        except Exception:
            pass

    @client.on(events.NewMessage(pattern=rf"\{prefix}tw ?(.*)", outgoing=True))
    async def tw_handler(event):
        arg = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()

        try:
            if reply:
                user = await reply.get_sender()
            elif arg:
                user = await client.get_entity(arg)
            else:
                await event.edit("❌ Укажи @username или ответь на сообщение")
                return

            uid = str(user.id)
            history = _cache.get(uid, [])
            first = getattr(user, "first_name", "") or ""
            last = getattr(user, "last_name", "") or ""
            current_name = f"{first} {last}".strip()
            current_username = f"@{user.username}" if getattr(user, "username", None) else "—"

            if not history:
                await event.edit(
                    f"👤 **{current_name}**\n\n"
                    f"📭 **История пуста**\n"
                    f"_Модуль начнёт собирать данные с этого момента_"
                )
                return

            lines = [
                f"⏳ **TimeWarp — история профиля**\n"
                f"👤 **Текущее имя:** {current_name}\n"
                f"🔗 **Username:** {current_username}\n\n"
                f"📜 **История изменений:**\n"
            ]
            for i, entry in enumerate(reversed(history[-10:])):
                name_e = entry.get("name", "—")
                uname = entry.get("username", "")
                uname_e = f"@{uname}" if uname else "—"
                date = entry.get("date", "—")
                lines.append(f"**{i+1}.** {name_e} | {uname_e}\n    📅 _{date}_")

            await event.edit("\n".join(lines))

        except Exception as e:
            await event.edit(f"❌ {e}")
