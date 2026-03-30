import aiohttp
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}ask ?([\s\S]*)", outgoing=True))
    async def ask_handler(event):
        question = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()
        if not question and reply and reply.text:
            question = reply.text.strip()
        if not question:
            await event.edit("❌ Задай вопрос: `.ask Как работает чёрная дыра?`")
            return

        await event.edit("🤖 **Думаю...**")
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://api.pollinations.ai/v1/chat/completions",
                    json={
                        "model": "openai",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "Ты умный помощник. Отвечай кратко и по делу. "
                                    "Если вопрос на русском — отвечай на русском."
                                ),
                            },
                            {"role": "user", "content": question},
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as r:
                    if r.status != 200:
                        raise Exception(f"HTTP {r.status}")
                    data = await r.json()

            answer = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )

            if not answer:
                raise Exception("Пустой ответ от AI")

            await event.edit(
                f"🤖 **Вопрос:** {question}\n\n"
                f"💬 **Ответ:**\n{answer}"
            )

        except Exception as e:
            await event.edit(f"❌ {e}")
