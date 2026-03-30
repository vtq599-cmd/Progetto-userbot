import pytz
from datetime import datetime
from telethon import events

CITIES = {
    "москва": "Europe/Moscow", "msk": "Europe/Moscow",
    "лондон": "Europe/London", "london": "Europe/London",
    "нью-йорк": "America/New_York", "ny": "America/New_York",
    "токио": "Asia/Tokyo", "tokyo": "Asia/Tokyo",
    "берлин": "Europe/Berlin", "berlin": "Europe/Berlin",
    "дубай": "Asia/Dubai", "dubai": "Asia/Dubai",
    "новосибирск": "Asia/Novosibirsk",
    "екатеринбург": "Asia/Yekaterinburg",
    "владивосток": "Asia/Vladivostok",
    "киев": "Europe/Kiev", "минск": "Europe/Minsk",
}

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}time ?(.*)", outgoing=True))
    async def time_handler(event):
        query = event.pattern_match.group(1).strip().lower()
        if not query:
            utc_now = datetime.now(pytz.utc)
            msk_now = utc_now.astimezone(pytz.timezone("Europe/Moscow"))
            fmt = "%H:%M:%S %d.%m.%Y"
            await event.edit(
                f"🕐 **Текущее время**\n\n"
                f"🌍 UTC: `{utc_now.strftime(fmt)}`\n"
                f"🇷🇺 МСК: `{msk_now.strftime(fmt)}`"
            )
            return
        tz_name = CITIES.get(query, query)
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            await event.edit(f"🕐 **{query.title()}:** `{now.strftime('%H:%M:%S %d.%m.%Y %Z')}`")
        except Exception:
            await event.edit(f"❌ Неизвестный город: `{query}`")
