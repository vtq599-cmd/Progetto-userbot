from telethon import events

_active = False

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}ghost ?(.*)", outgoing=True))
    async def ghost_handler(event):
        global _active
        arg = event.pattern_match.group(1).strip().lower()

        if arg == "on":
            if _active:
                return await event.edit("👻 Ghost Mode уже включён")
            _active = True
            original = client.mark_read
            client._orig_mark_read = original
            async def fake_read(*args, **kwargs):
                return None
            client.mark_read = fake_read
            await event.edit("👻 **Ghost Mode включён**\nСообщения не будут отмечаться как прочитанные")

        elif arg == "off":
            if not _active:
                return await event.edit("👁 Ghost Mode уже выключён")
            _active = False
            if hasattr(client, "_orig_mark_read"):
                client.mark_read = client._orig_mark_read
            await event.edit("👁 **Ghost Mode выключён**")

        else:
            status = "включён 👻" if _active else "выключён 👁"
            await event.edit(
                f"ℹ️ Ghost Mode: **{status}**\n"
                f"`.ghost on` / `.ghost off`"
            )
