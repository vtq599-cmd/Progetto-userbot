from datetime import datetime
import re
from zoneinfo import ZoneInfo, available_timezones

from telethon import events


CITIES = {
    "москва": "Europe/Moscow",
    "мск": "Europe/Moscow",
    "волгоград": "Europe/Volgograd",
    "самара": "Europe/Samara",
    "саратов": "Europe/Saratov",
    "уфа": "Asia/Yekaterinburg",
    "пермь": "Asia/Yekaterinburg",
    "челябинск": "Asia/Yekaterinburg",
    "калининград": "Europe/Kaliningrad",
    "санкт-петербург": "Europe/Moscow",
    "питер": "Europe/Moscow",
    "казань": "Europe/Moscow",
    "нижний новгород": "Europe/Moscow",
    "ростов-на-дону": "Europe/Moscow",
    "воронеж": "Europe/Moscow",
    "краснодар": "Europe/Moscow",
    "сочи": "Europe/Moscow",
    "минск": "Europe/Minsk",
    "киев": "Europe/Kyiv",
    "астана": "Asia/Almaty",
    "алматы": "Asia/Almaty",
    "ташкент": "Asia/Tashkent",
    "бишкек": "Asia/Bishkek",
    "ереван": "Asia/Yerevan",
    "тбилиси": "Asia/Tbilisi",
    "баку": "Asia/Baku",
    "лондон": "Europe/London",
    "берлин": "Europe/Berlin",
    "париж": "Europe/Paris",
    "рим": "Europe/Rome",
    "мадрид": "Europe/Madrid",
    "амстердам": "Europe/Amsterdam",
    "стамбул": "Europe/Istanbul",
    "нью-йорк": "America/New_York",
    "лос-анджелес": "America/Los_Angeles",
    "чикаго": "America/Chicago",
    "торонто": "America/Toronto",
    "ванкувер": "America/Vancouver",
    "мехико": "America/Mexico_City",
    "сан-паулу": "America/Sao_Paulo",
    "дубай": "Asia/Dubai",
    "эр-рияд": "Asia/Riyadh",
    "тель-авив": "Asia/Jerusalem",
    "токио": "Asia/Tokyo",
    "пекин": "Asia/Shanghai",
    "сеул": "Asia/Seoul",
    "бангкок": "Asia/Bangkok",
    "дели": "Asia/Kolkata",
    "мумбаи": "Asia/Kolkata",
    "сингапур": "Asia/Singapore",
    "гонконг": "Asia/Hong_Kong",
    "джакарта": "Asia/Jakarta",
    "сидней": "Australia/Sydney",
    "мельбурн": "Australia/Melbourne",
    "окленд": "Pacific/Auckland",
    "новосибирск": "Asia/Novosibirsk",
    "екатеринбург": "Asia/Yekaterinburg",
    "омск": "Asia/Omsk",
    "красноярск": "Asia/Krasnoyarsk",
    "иркутск": "Asia/Irkutsk",
    "якутск": "Asia/Yakutsk",
    "владивосток": "Asia/Vladivostok",
    "магадан": "Asia/Magadan",
    "камчатка": "Asia/Kamchatka",
}


def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}time(?:\s+(.+))?$", outgoing=True))
    async def time_handler(event):
        query = (event.pattern_match.group(1) or "").strip().lower()
        if not query:
            query = "Москва"
        zone = CITIES.get(query, query)
        try:
            if zone not in available_timezones():
                raise ValueError
            now = datetime.now(ZoneInfo(zone))
            await event.edit(
                f"🕐 **{query.title()}**\n"
                f"`{now.strftime('%H:%M:%S %d.%m.%Y %Z')}`"
            )
        except Exception:
            await event.edit(
                "❌ Город не найден. Можно написать город из списка "
                "или timezone вроде `Europe/Moscow`."
            )