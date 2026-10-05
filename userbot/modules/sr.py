import asyncio
import re
import time

from telethon import events

from modules.ai import text_answer


_active = False
_last_reply = {}


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}sr(?:\s+(on|off))?$", outgoing=True))
    async def sr_command(event):
        global _active
        action = (event.pattern_match.group(1) or "").lower()
        if action == "on":
            _active = True
            return await event.edit("🤖 SmartReply **включён**")
        if action == "off":
            _active = False
            return await event.edit("😴 SmartReply **выключен**")
        status = "включён" if _active else "выключен"
        await event.edit(f"ℹ️ SmartReply: **{status}**\n`.sr on` / `.sr off`")

    @client.on(events.NewMessage(incoming=True, func=lambda event: event.is_private))
    async def sr_watcher(event):
        if not _active or not event.text:
            return
        now = time.monotonic()
        if now - _last_reply.get(event.sender_id, 0) < 60:
            return
        _last_reply[event.sender_id] = now
        try:
            reply = await text_answer(
                f"Ответь кратко и вежливо, что я временно недоступен и отвечу позже. "
                f"Сообщение собеседника: {event.text}"
            )
            await client.send_message(event.chat_id, f"🤖 {reply}")
        except Exception:
            _last_reply.pop(event.sender_id, None)