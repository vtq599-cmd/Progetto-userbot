from telethon import events

def register(client, prefix):
    @client.on(events.NewMessage(pattern=rf"\{prefix}first ?(.*)", outgoing=True))
    async def first_handler(event):
        arg = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()

        await event.edit("🔍 **Ищу первое сообщение...**")
        try:
            from_user = None

            if arg:
                try:
                    from_user = await client.get_entity(arg)
                except Exception:
                    await event.edit(f"❌ Пользователь **{arg}** не найден")
                    return
            elif reply:
                from_user = await reply.get_sender()

            if from_user:
                first = None
                async for msg in client.iter_messages(
                    event.chat_id, from_user=from_user.id, reverse=True, limit=1
                ):
                    first = msg

                if not first:
                    await event.edit("❌ Сообщений не найдено")
                    return

                name = (
                    f"{getattr(from_user, 'first_name', '') or ''} "
                    f"{getattr(from_user, 'last_name', '') or ''}".strip()
                    or str(from_user.id)
                )
                date_str = first.date.strftime("%d.%m.%Y %H:%M")
                text = (first.text or "[медиа]")[:200]
                chat_id = str(event.chat_id).replace("-100", "")

                await event.edit(
                    f"📜 **Первое сообщение от {name}**\n\n"
                    f"📅 **Дата:** {date_str}\n"
                    f"💬 **Текст:** {text}\n\n"
                    f"🔗 [Перейти к сообщению](https://t.me/c/{chat_id}/{first.id})"
                )

            else:
                first = None
                async for msg in client.iter_messages(event.chat_id, reverse=True, limit=1):
                    first = msg

                if not first:
                    await event.edit("❌ Сообщений не найдено")
                    return

                sender = await first.get_sender()
                name = "—"
                if sender:
                    name = (
                        f"{getattr(sender, 'first_name', '') or ''} "
                        f"{getattr(sender, 'last_name', '') or ''}".strip()
                        or str(sender.id)
                    )

                date_str = first.date.strftime("%d.%m.%Y %H:%M")
                text = (first.text or "[медиа]")[:200]
                chat_id = str(event.chat_id).replace("-100", "")

                await event.edit(
                    f"📜 **Первое сообщение в чате**\n\n"
                    f"👤 **Автор:** {name}\n"
                    f"📅 **Дата:** {date_str}\n"
                    f"💬 **Текст:** {text}\n\n"
                    f"🔗 [Перейти к сообщению](https://t.me/c/{chat_id}/{first.id})"
                )

        except Exception as e:
            await event.edit(f"❌ {e}")
