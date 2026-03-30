import aiohttp
from urllib.parse import quote
from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}lyrics ?([\s\S]*)", outgoing=True))
    async def lyrics_handler(event):
        args = event.pattern_match.group(1).strip()
        if not args:
            await event.edit(
                "❌ **Использование:**\n"
                "`.lyrics Imagine Dragons - Believer`\n"
                "`.lyrics Моргенштерн - Cristal`"
            )
            return

        await event.edit("🎵 **Ищу текст песни...**")
        try:
            if " - " in args:
                artist, title = args.split(" - ", 1)
                artist, title = artist.strip(), title.strip()
            else:
                words = args.split()
                artist = words[0]
                title = " ".join(words[1:]) if len(words) > 1 else args

            lyrics = ""
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://api.lyrics.ovh/v1/{quote(artist)}/{quote(title)}",
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        lyrics = data.get("lyrics", "")

                if not lyrics:
                    async with s.get(
                        f"https://some-random-api.com/lyrics?title={quote(args)}",
                        timeout=aiohttp.ClientTimeout(total=15),
                    ) as r:
                        data = await r.json()
                        lyrics = data.get("lyrics", "")
                        artist = data.get("author", artist)
                        title = data.get("title", title)

            if not lyrics:
                await event.edit(
                    "❌ **Текст песни не найден**\n"
                    "Попробуй формат: `.lyrics Исполнитель - Название`"
                )
                return

            header = f"🎵 **{artist}** — **{title}**\n\n"
            max_len = 4096 - len(header) - 50
            if len(lyrics) > max_len:
                lyrics = lyrics[:max_len] + "\n\n_... (текст обрезан)_"

            await event.edit(header + lyrics)

        except Exception as e:
            await event.edit(f"❌ {e}")
