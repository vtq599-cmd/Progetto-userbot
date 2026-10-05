import asyncio
from datetime import datetime, timedelta, timezone
import re

from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights


FULL_BAN = ChatBannedRights(until_date=None, view_messages=True)
FULL_UNBAN = ChatBannedRights(
    until_date=None,
    view_messages=False,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    embed_links=False,
)
_warns = {}


def name_of(user):
    return (
        f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
        or str(user.id)
    )


async def target(event):
    reply = await event.get_reply_message()
    return await reply.get_sender() if reply else None


def mute_rights(until):
    return ChatBannedRights(
        until_date=until,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )


def register(client, prefix):
    async def require_target(event):
        if not (event.is_group or event.is_channel):
            await event.edit("❌ Только в группах и каналах.")
            return None
        user = await target(event)
        if not user:
            await event.edit("❌ Ответь на сообщение пользователя.")
            return None
        return user

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}(kick|ban|unban)$", outgoing=True))
    async def ban_commands(event):
        user = await require_target(event)
        if not user:
            return
        action = event.pattern_match.group(1)
        try:
            chat = await event.get_input_chat()
            if action == "kick":
                await client(EditBannedRequest(chat, user.id, FULL_BAN))
                await asyncio.sleep(1)
                await client(EditBannedRequest(chat, user.id, FULL_UNBAN))
                text = f"👢 {name_of(user)} кикнут"
            elif action == "ban":
                await client(EditBannedRequest(chat, user.id, FULL_BAN))
                text = f"🔨 {name_of(user)} забанен"
            else:
                await client(EditBannedRequest(chat, user.id, FULL_UNBAN))
                text = f"✅ {name_of(user)} разбанен"
            await event.edit(text)
        except Exception as exc:
            await event.edit(f"❌ {exc}")

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}(mute)(?:\s+(\d+))?$", outgoing=True))
    async def mute_command(event):
        user = await require_target(event)
        if not user:
            return
        minutes = int(event.pattern_match.group(2) or 0)
        until = datetime.now(timezone.utc) + timedelta(minutes=minutes) if minutes else None
        try:
            await client(
                EditBannedRequest(
                    await event.get_input_chat(),
                    user.id,
                    mute_rights(until),
                )
            )
            duration = f"на {minutes} мин." if minutes else "навсегда"
            await event.edit(f"🔇 {name_of(user)} замучен {duration}")
        except Exception as exc:
            await event.edit(f"❌ {exc}")

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}unmute$", outgoing=True))
    async def unmute_command(event):
        user = await require_target(event)
        if user:
            try:
                await client(EditBannedRequest(await event.get_input_chat(), user.id, FULL_UNBAN))
                await event.edit(f"🔊 {name_of(user)} размучен")
            except Exception as exc:
                await event.edit(f"❌ {exc}")

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}warn$", outgoing=True))
    async def warn_command(event):
        user = await require_target(event)
        if not user:
            return
        chat_id = str(event.chat_id)
        user_id = str(user.id)
        current = _warns.setdefault(chat_id, {}).get(user_id, 0) + 1
        _warns[chat_id][user_id] = current
        if current >= 3:
            _warns[chat_id][user_id] = 0
            try:
                await client(EditBannedRequest(await event.get_input_chat(), user.id, FULL_BAN))
                await event.edit(f"🔨 {name_of(user)} получил 3/3 и забанен")
            except Exception as exc:
                await event.edit(f"❌ Не удалось забанить: {exc}")
        else:
            await event.edit(f"⚠️ {name_of(user)}: {'🟥' * current}{'⬜️' * (3 - current)} {current}/3")

    @client.on(events.NewMessage(pattern=rf"^{re.escape(prefix)}unwarned$", outgoing=True))
    async def unwarned_command(event):
        user = await require_target(event)
        if not user:
            return
        chat_id = str(event.chat_id)
        user_id = str(user.id)
        current = _warns.setdefault(chat_id, {}).get(user_id, 0)
        if current <= 1:
            _warns[chat_id].pop(user_id, None)
            text = f"✅ У {name_of(user)} снято последнее предупреждение"
        else:
            _warns[chat_id][user_id] = current - 1
            text = f"✅ У {name_of(user)} осталось {_warns[chat_id][user_id]}/3 предупреждений"
        await event.edit(text)