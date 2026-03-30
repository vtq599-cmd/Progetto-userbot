import aiohttp
from telethon import events

_active = False
_replied = set()

async def _get_ai_reply(my_name, user_name, text):
    async with aiohttp.ClientSession() as s:
        async with s.post(
            "https://api.pollinations.ai/v1/chat/completions",
            json={
                "model": "openai",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"Ты — {my_name} в Telegram. Сейчас ты недоступен. "
                            "Отвечай кратко и вежливо, что тебя нет и ты ответишь позже. "
                            "Отвечай на том же языке что и собеседник. Не более 2 предложений."
                        ),
                    },
                    {"role": "user", "content": f"{user_name} написал: {text}"},
                ],
            },
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as r:
            data = await r.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}sr ?(.*)", outgoing=True))
    async def sr_cmd(event):
        global _active, _replied
        arg = event.pattern_match.group(1).strip().lower()

        if arg.startswith("on"):
            if _active:
                return await event.edit("🤖 SmartReply уже включён")
            _active = True
            _replied.clear()
            await event.edit("🤖 **SmartReply включён**\nAI будет отвечать на сообщения в ЛС")

        elif arg.startswith("off"):
            if not _active:
                return await event.edit("😴 SmartReply уже выключён")
            _active = False
            await event.edit("😴 **SmartReply выключён**")

        else:
            status = "включён 🤖" if _active else "выключён 😴"
            await event.edit(f"ℹ️ SmartReply: **{status}**\n`.sr on` / `.sr off`")

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def sr_watcher(event):
        global _replied
        if not _active or event.out:
            return
        sender_id = event.sender_id
        if sender_id in _replied or not event.text:
            return
        try:
            me = await client.get_me()
            my_name = me.first_name or "User"
            sender = await event.get_sender()
            user_name = getattr(sender, "first_name", "") or str(sender_id)
            reply = await _get_ai_reply(my_name, user_name, event.text)
            if not reply:
                return
            _replied.add(sender_id)
            await client.send_message(event.chat_id, f"🤖 {reply}")
        except Exception:
            pass
