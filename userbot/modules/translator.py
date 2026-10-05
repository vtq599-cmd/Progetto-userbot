import re

import aiohttp
from telethon import events


async def translate(text, target):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status != 200:
                raise RuntimeError(f"Переводчик HTTP {response.status}")
            data = await response.json(content_type=None)
    result = "".join(item[0] for item in data[0] if item[0])
    return result, data[2]


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}(?:tr|translate)(?:\s+([a-zA-Z-]+))?\s*([\s\S]*)$", outgoing=True))
    async def translate_handler(event):
        target = event.pattern_match.group(1) or "ru"
        text = (event.pattern_match.group(2) or "").strip()
        reply = await event.get_reply_message()
        if not text and reply:
            text = reply.text or ""
        if not text:
            return await event.edit(
                f"Ответь на текст или напиши `{prefix}tr en текст`."
            )
        await event.edit("🌐 Перевожу...")
        try:
            result, source = await translate(text, target)
            await event.edit(
                f"🌐 {source} → {target}\n\n{result}",
                parse_mode=None,
            )
        except Exception as exc:
            await event.edit(f"❌ Перевод: {exc}")