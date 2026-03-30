from datetime import datetime
from telethon import events

_afk = False
_afk_reason = ""
_afk_since = None
_notified = set()

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}afk ?(.*)", outgoing=True))
    async def set_afk(event):
        global _afk, _afk_reason, _afk_since, _notified
        _afk = True
        _afk_reason = event.pattern_match.group(1).strip() or "Нет причины"
        _afk_since = datetime.now()
        _notified = set()
        await event.edit(f"😴 **AFK включён**\nПричина: {_afk_reason}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}unafk", outgoing=True))
    async def unset_afk(event):
        global _afk
        if not _afk:
            await event.edit("❗ AFK не активен.")
            return
        minutes = int((datetime.now() - _afk_since).total_seconds() // 60)
        _afk = False
        await event.edit(f"✅ **AFK выключен**\nОтсутствовал: {minutes} мин.")

    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        if not _afk:
            return
        sender_id = event.sender_id
        if not sender_id or sender_id in _notified:
            return
        if not event.is_private and not event.mentioned:
            return
        _notified.add(sender_id)
        minutes = int((datetime.now() - _afk_since).total_seconds() // 60)
        await event.reply(f"😴 AFK ({minutes} мин.)\nПричина: {_afk_reason}")
