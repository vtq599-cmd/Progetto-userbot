import asyncio
from telethon import events
from telethon.tl.functions.account import UpdateStatusRequest

_task = None
_active = False

def register(client, prefix):
    global _task, _active

    async def online_loop():
        while _active:
            try:
                await client(UpdateStatusRequest(offline=False))
            except Exception:
                pass
            await asyncio.sleep(60)

    @client.on(events.NewMessage(pattern=rf"\{prefix}onl", outgoing=True))
    async def onl_handler(event):
        global _task, _active
        args = event.raw_text.split(maxsplit=1)
        arg = args[1].strip().lower() if len(args) > 1 else ""

        if arg == "on":
            if _active:
                return await event.edit("✅ Онлайн уже включён")
            _active = True
            _task = asyncio.ensure_future(online_loop())
            await event.edit("✅ Бесконечный онлайн **включён**")

        elif arg == "off":
            if not _active:
                return await event.edit("❌ Онлайн уже выключён")
            _active = False
            if _task:
                _task.cancel()
                _task = None
            await client(UpdateStatusRequest(offline=True))
            await event.edit("❌ Бесконечный онлайн **выключён**")

        else:
            await event.edit("❓ Используй: `.onl on` или `.onl off`")
