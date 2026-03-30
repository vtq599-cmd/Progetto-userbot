import asyncio
from datetime import datetime, timezone, timedelta
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
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

def mute_rights(until=None):
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

_warns = {}

async def get_target(event):
    reply = await event.get_reply_message()
    if not reply:
        return None
    return await reply.get_sender()

def get_name(user):
    first = getattr(user, "first_name", "") or ""
    last = getattr(user, "last_name", "") or ""
    return f"{first} {last}".strip() or str(user.id)

async def get_invite(client, event):
    try:
        result = await client(ExportChatInviteRequest(peer=await event.get_input_chat()))
        return result.link
    except Exception:
        try:
            chat = await event.get_chat()
            if getattr(chat, "username", None):
                return f"https://t.me/{chat.username}"
        except Exception:
            pass
    return None

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}kick$", outgoing=True))
    async def kick_handler(event):
        if not (event.is_group or event.is_channel):
            return await event.edit("❌ Только в группах")
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        try:
            chat = await event.get_input_chat()
            await client(EditBannedRequest(channel=chat, participant=user.id, banned_rights=FULL_BAN))
            await asyncio.sleep(1)
            await client(EditBannedRequest(channel=chat, participant=user.id, banned_rights=FULL_UNBAN))
            await event.edit(f"👢 {name} был кикнут")
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}ban$", outgoing=True))
    async def ban_handler(event):
        if not (event.is_group or event.is_channel):
            return await event.edit("❌ Только в группах")
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        try:
            chat = await event.get_input_chat()
            await client(EditBannedRequest(channel=chat, participant=user.id, banned_rights=FULL_BAN))
            await event.edit(f"🔨 {name} забанен")
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}unban$", outgoing=True))
    async def unban_handler(event):
        if not (event.is_group or event.is_channel):
            return await event.edit("❌ Только в группах")
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        try:
            chat_input = await event.get_input_chat()
            await client(EditBannedRequest(channel=chat_input, participant=user.id, banned_rights=FULL_UNBAN))
            await event.edit(f"✅ {name} разбанен")

            invite = await get_invite(client, event)
            chat = await event.get_chat()
            chat_name = getattr(chat, "title", "чат")
            if invite:
                try:
                    await client.send_message(
                        user.id,
                        f"✅ Вы были разбанены в чате «{chat_name}»\n\n🔗 Ссылка для входа: {invite}"
                    )
                except Exception:
                    pass
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}mute ?(\d*)", outgoing=True))
    async def mute_handler(event):
        if not (event.is_group or event.is_channel):
            return await event.edit("❌ Только в группах")
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        arg = event.pattern_match.group(1).strip()
        until = None
        time_str = "навсегда"
        if arg.isdigit():
            minutes = int(arg)
            until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            if minutes < 60:
                time_str = f"{minutes} мин."
            elif minutes < 1440:
                time_str = f"{minutes // 60} ч."
            else:
                time_str = f"{minutes // 1440} дн."
        try:
            chat = await event.get_input_chat()
            await client(EditBannedRequest(channel=chat, participant=user.id, banned_rights=mute_rights(until)))
            await event.edit(f"🔇 {name} замучен на {time_str}")
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}unmute$", outgoing=True))
    async def unmute_handler(event):
        if not (event.is_group or event.is_channel):
            return await event.edit("❌ Только в группах")
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        try:
            chat = await event.get_input_chat()
            await client(EditBannedRequest(channel=chat, participant=user.id, banned_rights=FULL_UNBAN))
            await event.edit(f"🔊 {name} размучен")
        except Exception as e:
            await event.edit(f"❌ {e}")

    @client.on(events.NewMessage(pattern=rf"\{prefix}warn$", outgoing=True))
    async def warn_handler(event):
        if not (event.is_group or event.is_channel):
            return await event.edit("❌ Только в группах")
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        chat_id = str(event.chat_id)
        uid = str(user.id)

        _warns.setdefault(chat_id, {})
        _warns[chat_id][uid] = _warns[chat_id].get(uid, 0) + 1
        count = _warns[chat_id][uid]

        if count >= 3:
            _warns[chat_id][uid] = 0
            try:
                chat = await event.get_input_chat()
                await client(EditBannedRequest(channel=chat, participant=user.id, banned_rights=FULL_BAN))
                await event.edit(
                    f"🔨 {name} получил 3/3 предупреждения\n"
                    f"⛔️ Автоматически забанен!"
                )
            except Exception as e:
                await event.edit(f"❌ Не удалось забанить: {e}")
        else:
            bars = "🟥" * count + "⬜️" * (3 - count)
            extra = "\n🔨 _Следующий варн = бан!_" if count == 2 else ""
            await event.edit(
                f"⚠️ {name} получает предупреждение\n\n"
                f"{bars} {count}/3{extra}"
            )

    @client.on(events.NewMessage(pattern=rf"\{prefix}unwarned$", outgoing=True))
    async def unwarned_handler(event):
        user = await get_target(event)
        if not user:
            return await event.edit("❌ Ответь на сообщение пользователя")
        name = get_name(user)
        chat_id = str(event.chat_id)
        uid = str(user.id)
        if chat_id in _warns:
            _warns[chat_id].pop(uid, None)
        await event.edit(f"✅ Предупреждения {name} сброшены")

    @client.on(events.NewMessage(pattern=rf"\{prefix}warnlist$", outgoing=True))
    async def warnlist_handler(event):
        chat_id = str(event.chat_id)
        chat_warns = _warns.get(chat_id, {})
        active = {uid: c for uid, c in chat_warns.items() if c > 0}
        if not active:
            return await event.edit("✅ Предупреждений нет")
        lines = ["⚠️ Предупреждения в чате:\n"]
        for uid, count in active.items():
            bars = "🟥" * count + "⬜️" * (3 - count)
            try:
                user = await client.get_entity(int(uid))
                name = get_name(user)
            except Exception:
                name = uid
            lines.append(f"👤 {name}: {bars} {count}/3")
        await event.edit("\n".join(lines))
