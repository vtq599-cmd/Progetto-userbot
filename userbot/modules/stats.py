from collections import Counter
from datetime import datetime, timedelta, timezone
import re

from telethon import events


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}stats(?:\s+(\d+))?$", outgoing=True))
    async def stats_handler(event):
        days = min(int(event.pattern_match.group(1) or 7), 30)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        counts = Counter()
        async for message in client.iter_messages(event.chat_id, limit=500):
            if message.date and message.date < since:
                break
            if message.sender_id:
                counts[message.sender_id] += 1
        if not counts:
            return await event.edit("📊 Нет сообщений за этот период.")
        lines = [f"📊 **Статистика за {days} дн.**"]
        for index, (user_id, count) in enumerate(counts.most_common(5), start=1):
            try:
                user = await client.get_entity(user_id)
                name = (
                    f"{getattr(user, 'first_name', '') or ''} "
                    f"{getattr(user, 'last_name', '') or ''}".strip()
                    or str(user_id)
                )
            except Exception:
                name = str(user_id)
            lines.append(f"{index}. [{name}](tg://user?id={user_id}) — `{count}`")
        await event.edit("\n".join(lines))