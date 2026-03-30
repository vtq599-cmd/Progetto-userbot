from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}alive", outgoing=True))
    async def alive_handler(event):
        me = await client.get_me()
        text = (
            "🤖 **Userbot активен!**\n\n"
            f"👤 Аккаунт: [{me.first_name}](tg://user?id={me.id})\n"
            f"⚡ Префикс: `{prefix}`\n"
            f"📦 Версия: `1.0`\n"
            "🔧 На базе: Telethon"
        )
        await event.edit(text)
