import re
from urllib.parse import quote

import aiohttp
from telethon import events


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}weather(?:\s+(.+))$", outgoing=True))
    async def weather_handler(event):
        city = event.pattern_match.group(1).strip()
        await event.edit("🌤 Получаю погоду...")
        try:
            url = f"https://wttr.in/{quote(city)}"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params={"format": "j1"},
                    headers={"User-Agent": "TelegramUserbot/1.0"},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"HTTP {response.status}")
                    data = await response.json(content_type=None)
            current = data["current_condition"][0]
            description = current["weatherDesc"][0]["value"]
            await event.edit(
                f"🌤 {city}\n"
                f"🌡 {current['temp_C']}°C (ощущается {current['FeelsLikeC']}°C)\n"
                f"☁️ {description}\n"
                f"💧 Влажность {current['humidity']}%\n"
                f"💨 Ветер {current['windspeedKmph']} км/ч",
                parse_mode=None,
            )
        except Exception as exc:
            await event.edit(f"❌ Погода: {exc}")