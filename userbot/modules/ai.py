import os
import re
import tempfile
from urllib.parse import quote

import aiohttp
from telethon import events


API_KEY = os.environ.get("POLLINATIONS_API_KEY", "").strip()
API_BASE = "https://gen.pollinations.ai"


def _headers():
    if not API_KEY:
        raise RuntimeError(
            "Добавь POLLINATIONS_API_KEY в userbot/.env — генерация AI требует ключ."
        )
    return {"Authorization": f"Bearer {API_KEY}"}


async def text_answer(prompt):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/v1/chat/completions",
            json={
                "model": "openai",
                "messages": [
                    {
                        "role": "system",
                        "content": "Отвечай ясно, кратко и на языке пользователя.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            headers=_headers(),
            timeout=aiohttp.ClientTimeout(total=120),
        ) as response:
            if response.status != 200:
                detail = (await response.text())[:300]
                raise RuntimeError(f"AI HTTP {response.status}: {detail}")
            data = await response.json()
    answer = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    if not answer:
        raise RuntimeError("AI вернул пустой ответ")
    return answer


async def image_file(prompt):
    url = f"{API_BASE}/image/{quote(prompt, safe='')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            params={"model": "flux", "width": 1024, "height": 1024, "nologo": "true"},
            headers=_headers(),
            timeout=aiohttp.ClientTimeout(total=240),
        ) as response:
            if response.status != 200:
                detail = (await response.text())[:300]
                raise RuntimeError(f"AI image HTTP {response.status}: {detail}")
            content_type = response.headers.get("Content-Type", "").lower()
            suffix = ".png" if "png" in content_type else ".jpg"
            data = await response.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as output:
        output.write(data)
        return output.name


def register(client, prefix):
    @client.on(
        events.NewMessage(
            pattern=rf"^{re.escape(prefix)}ai(?:\s+([\s\S]*))?$",
            outgoing=True,
        )
    )
    async def ai_handler(event):
        prompt = (event.pattern_match.group(1) or "").strip()
        reply = await event.get_reply_message()
        if not prompt and reply and reply.text:
            prompt = reply.text.strip()
        if not prompt:
            return await event.edit(
                f"Использование: `{prefix}ai вопрос` или "
                f"`{prefix}ai image описание`"
            )

        image_mode = False
        lowered = prompt.lower()
        for marker in ("image ", "img ", "картинка ", "изображение "):
            if lowered.startswith(marker):
                image_mode = True
                prompt = prompt[len(marker):].strip()
                break
        if not prompt:
            return await event.edit("Добавь описание запроса.")

        await event.edit("🎨 Генерирую изображение..." if image_mode else "🤖 Думаю...")
        tmp = None
        try:
            if image_mode:
                tmp = await image_file(prompt)
                await event.delete()
                await client.send_file(
                    event.chat_id, tmp, caption=f"🎨 {prompt}", parse_mode=None
                )
            else:
                await event.edit(
                    f"🤖 AI\n\n{await text_answer(prompt)}",
                    parse_mode=None,
                )
        except Exception as exc:
            await event.edit(f"❌ AI: {exc}")
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
