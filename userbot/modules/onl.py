import asyncio
import re

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
            await asyncio.sleep(50)

    @client.on(
        events.NewMessage(
            pattern=rf"^{re.escape(prefix)}onl(?:\s+(on|off))?$",
            outgoing=True,
        )
    )
    async def onl_handler(event):
        global _task, _active
        action = (event.pattern_match.group(1) or "").lower()
        if action == "on":
            if _active:
                return await event.edit("✅ Онлайн уже включён")
            _active = True
            _task = asyncio.create_task(online_loop())
            return await event.edit("✅ Онлайн **включён**")
        if action == "off":
            if not _active:
                return await event.edit("❌ Онлайн уже выключен")
            _active = False
            if _task:
                _task.cancel()
                _task = None
            await client(UpdateStatusRequest(offline=True))
            return await event.edit("❌ Онлайн **выключен**")
        status = "включён" if _active else "выключен"
        await event.edit(f"ℹ️ Онлайн: **{status}**\n`.onl on` / `.onl off`")