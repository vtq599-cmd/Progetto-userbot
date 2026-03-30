from telethon import events
from telethon.tl.functions.account import UpdateEmojiStatusRequest
from telethon.tl.types import EmojiStatus, EmojiStatusEmpty

PRESETS = {
    "🌙": 5373026167722876724,
    "⚡": 5361541227604874514,
    "🔥": 5373141891321699086,
    "❤️": 5471952986970267163,
    "👑": 5361590792955158062,
    "💎": 5471979153642551278,
    "🎮": 5373059590515785023,
    "🌟": 5471916052883276878,
    "🐱": 5373060526162792413,
    "🦊": 5373044735358058756,
    "☕": 5373078515358400446,
    "🍀": 5471956118519205364,
    "🌈": 5471947758819587675,
    "💤": 5373034472717068436,
}

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}estatus ?(.*)", outgoing=True))
    async def estatus_handler(event):
        arg = event.pattern_match.group(1).strip()

        if not arg:
            await event.edit(
                f"❌ Укажи эмодзи:\n`.estatus 🔥`\n`.estatus clear` — убрать\n\n"
                f"**Доступные:** {' '.join(PRESETS.keys())}"
            )
            return

        await event.edit("⚡️ **Устанавливаю статус...**")
        try:
            if arg.lower() == "clear":
                await client(UpdateEmojiStatusRequest(emoji_status=EmojiStatusEmpty()))
                await event.edit("✅ **Статус очищен!**")
                return

            document_id = PRESETS.get(arg) or PRESETS.get(arg[0])
            if not document_id:
                await event.edit(
                    f"❌ Эмодзи **{arg}** не найден\n"
                    f"Доступные: {' '.join(PRESETS.keys())}"
                )
                return

            await client(UpdateEmojiStatusRequest(emoji_status=EmojiStatus(document_id=document_id)))
            await event.edit(f"✅ **Статус установлен:** {arg}")

        except Exception as e:
            await event.edit(f"❌ {e}")
