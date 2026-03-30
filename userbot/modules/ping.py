"""
Модуль: ping
Команда: .ping — проверка работы бота
"""

from telethon import events

_client = None


def init(client):
    global _client
    _client = client

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping$"))
    async def ping_handler(event):
        await event.edit("🏓 Pong!")
