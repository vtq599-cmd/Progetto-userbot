import re

from telethon import events


_active = False
_original = {}


def register(client, prefix):
    global _active

    async def noop(*args, **kwargs):
        return None

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}ghost(?:\s+(on|off))?$", outgoing=True))
    async def ghost_handler(event):
        global _active
        action = (event.pattern_match.group(1) or "").lower()
        if action == "on":
            if not _active:
                for name in ("mark_read", "send_read_acknowledge"):
                    if hasattr(client, name):
                        _original[name] = getattr(client, name)
                        setattr(client, name, noop)
                _active = True
            return await event.edit("👻 Ghost Mode **включён**")
        if action == "off":
            for name, original in _original.items():
                setattr(client, name, original)
            _original.clear()
            _active = False
            return await event.edit("👁 Ghost Mode **выключен**")
        status = "включён" if _active else "выключен"
        await event.edit(f"ℹ️ Ghost Mode: **{status}**\n`.ghost on` / `.ghost off`")