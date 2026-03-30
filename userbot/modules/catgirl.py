import aiohttp
import io
from telethon import events

CATEGORIES = ["catgirl", "neko", "kitsune", "fox_girl", "wolf_girl"]

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}catgirl ?(.*)", outgoing=True))
    async def catgirl_handler(event):
        arg = event.pattern_match.group(1).strip().lower()
        category = arg if arg in CATEGORIES else "neko"

        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    f"https://nekos.best/api/v2/{category}",
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as r:
                    data = await r.json()

                img_url = data["results"][0]["url"]
                artist = data["results"][0].get("artist_name", "Unknown")

                async with s.get(img_url) as r:
                    img_bytes = await r.read()

            file = io.BytesIO(img_bytes)
            file.name = "catgirl.png"

            await event.delete()
            await client.send_file(
                event.chat_id,
                file,
                caption=f"😺 **{category.replace('_', ' ').title()}**\n🎨 {artist}"
            )
        except Exception as e:
            await event.edit(f"❌ {e}")
