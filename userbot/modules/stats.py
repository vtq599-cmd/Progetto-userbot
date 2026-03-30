from collections import defaultdict
from datetime import datetime, timedelta
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}stats ?(\d*)", outgoing=True))
    async def stats_handler(event):
        if not (event.is_group or event.is_channel):
            await event.edit("❌ Только для групп")
            return

        arg = event.pattern_match.group(1).strip()
        days = min(int(arg) if arg.isdigit() else 7, 30)

        await event.edit(f"📊 **Собираю статистику за {days} дней...**")

        try:
            since = datetime.now() - timedelta(days=days)
            counts = defaultdict(int)
            names = {}
            total = 0

            async for msg in client.iter_messages(event.chat_id, limit=3000):
                if not msg or not msg.date:
                    break
                if msg.date.replace(tzinfo=None) < since:
                    break
                if msg.sender_id and not getattr(msg.sender, "bot", False):
                    counts[msg.sender_id] += 1
                    total += 1
                    if msg.sender_id not in names:
                        sender = await msg.get_sender()
                        if sender:
                            names[msg.sender_id] = (
                                f"{getattr(sender, 'first_name', '') or ''} "
                                f"{getattr(sender, 'last_name', '') or ''}".strip()
                                or str(msg.sender_id)
                            )

            if not counts:
                return await event.edit("📭 **Нет данных за этот период**")

            top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
            medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
            lines = [f"📊 **Топ активных за {days} дней**\n"]

            for i, (uid, count) in enumerate(top):
                name = names.get(uid, str(uid))
                pct = round(count / total * 100)
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                lines.append(
                    f"{medals[i]} [{name}](tg://user?id={uid})\n"
                    f"    `{bar}` {count} ({pct}%)"
                )

            lines.append(f"\n💬 **Всего сообщений:** {total}")
            await event.edit("\n".join(lines))

        except Exception as e:
            await event.edit(f"❌ {e}")
