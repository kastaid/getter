# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl import functions as fun, types as typ
from . import (
    DEVS,
    kasta_cmd,
    plugins_help,
    hl,
    suppress,
    normalize_chat_id,
    mentionuser,
    display_name,
    format_exc,
    strip_emoji,
    time_formatter,
    until_time,
    normalize,
)


@kasta_cmd(
    pattern="ban(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Banning...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot ban to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to ban our awesome developers.`", time=3)
    is_reported = False
    with suppress(BaseException):
        if kst.is_group and kst.is_reply:
            is_reported = await ga(
                fun.channels.ReportSpamRequest(
                    chat_id,
                    participant=user.id,
                    id=[kst.reply_to_msg_id],
                )
            )
        else:
            is_reported = await ga.report_spam(user.id)
    try:
        await ga.edit_permissions(chat_id, user.id, view_messages=False)
        text = "{} banned and {} reported!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            "was" if is_reported else "not",
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="dban(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Dbanning...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to user message.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot dban to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to dban our awesome developers.`", time=3)
    is_reported = False
    with suppress(BaseException):
        if kst.is_group:
            is_reported = await ga(
                fun.channels.ReportSpamRequest(
                    chat_id,
                    participant=user.id,
                    id=[kst.reply_to_msg_id],
                )
            )
        else:
            is_reported = await ga.report_spam(user.id)
    try:
        await ga.edit_permissions(chat_id, user.id, view_messages=False)
        await (await kst.get_reply_message()).try_delete()
        text = "{} dbanned and {} reported!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            "was" if is_reported else "not",
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="sban(?: |$)(.*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    user, _ = await ga.get_user(kst)
    await kst.try_delete()
    if not user:
        return
    if user.id == ga.uid:
        return
    if user.id in DEVS:
        return
    with suppress(BaseException):
        if kst.is_group and kst.is_reply:
            await ga(
                fun.channels.ReportSpamRequest(
                    chat_id,
                    participant=user.id,
                    id=[kst.reply_to_msg_id],
                )
            )
        else:
            await ga.report_spam(user.id)
    with suppress(BaseException):
        await ga.edit_permissions(chat_id, user.id, view_messages=False)


@kasta_cmd(
    pattern="tban(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Tbanning...`")
    user, args = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot tban to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to tban our awesome developers.`", time=3)
    opts = args.split(" ")
    timing = opts[0].lower()
    if not timing:
        return await yy.eor("`Provide a timing to tban!`", time=5)
    reason = " ".join(opts[1:]).strip()
    until_date, duration = until_time(timing[:-1], timing[-1])
    try:
        await ga.edit_permissions(chat_id, user.id, until_date=until_date, view_messages=False)
        text = "{} temporarily banned!\n<b>Duration:</b> {}{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"{timing[:-1]} {duration}",
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="unban(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Unbanning...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot unban to myself.`", time=3)
    try:
        await ga.edit_permissions(chat_id, user.id)
        text = "{} unbanned!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="mute(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Muting...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot mute to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to mute our awesome developers.`", time=3)
    try:
        await ga.edit_permissions(chat_id, user.id, send_messages=False)
        text = "{} muted!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="dmute(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Dmuting...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to user message.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot dmute to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to dmute our awesome developers.`", time=3)
    reply = await kst.get_reply_message()
    try:
        await ga.edit_permissions(chat_id, user.id, send_messages=False)
        await reply.try_delete()
        text = "{} dmuted!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="smute(?: |$)(.*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    user, _ = await ga.get_user(kst)
    await kst.try_delete()
    if not user:
        return
    if user.id == ga.uid:
        return
    if user.id in DEVS:
        return
    with suppress(BaseException):
        await ga.edit_permissions(chat_id, user.id, send_messages=False)


@kasta_cmd(
    pattern="tmute(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Tmuting...`")
    user, args = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot tmute to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to tmute our awesome developers.`", time=3)
    opts = args.split(" ")
    timing = opts[0].lower()
    if not timing:
        return await yy.eor("`Provide a timing to tmute!`", time=5)
    reason = " ".join(opts[1:]).strip()
    until_date, duration = until_time(timing[:-1], timing[-1])
    try:
        await ga.edit_permissions(chat_id, user.id, until_date=until_date, send_messages=False)
        text = "{} temporarily muted!\n<b>Duration:</b> {}{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"{timing[:-1]} {duration}",
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="unmute(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Unmuting...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot unmute to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to unmute our awesome developers.`", time=3)
    try:
        await ga.edit_permissions(chat_id, user.id, send_messages=True)
        text = "{} unmuted!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="kick(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Kicking...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot kick to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to kick our awesome developers.`", time=3)
    try:
        await ga.kick_participant(chat_id, user.id)
        text = "{} kicked!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="dkick(?: |$)((?s).*)",
    admins_only=True,
    require="ban_users",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Dkicking...`")
    user, reason = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to user message.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot dkick to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to dkick our awesome developers.`", time=3)
    reply = await kst.get_reply_message()
    try:
        await ga.kick_participant(chat_id, user.id)
        await reply.try_delete()
        text = "{} dkicked!{}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            f"\n<b>Reason:</b> <pre>{reason}</pre>" if reason else "",
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="skick(?: |$)(.*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    user, _ = await ga.get_user(kst)
    await kst.try_delete()
    if not user:
        return
    if user.id == ga.uid:
        return
    if user.id in DEVS:
        return
    with suppress(BaseException):
        await ga.kick_participant(kst.chat_id, user.id)


@kasta_cmd(
    pattern="lock$",
    admins_only=True,
)
async def _(kst):
    try:
        await kst.client.edit_permissions(
            kst.chat_id,
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_inline=False,
            embed_link_previews=False,
            send_polls=False,
            change_info=False,
            invite_users=False,
            pin_messages=False,
        )
        await kst.eor("`locked`", time=5)
    except Exception as err:
        await kst.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="unlock(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    match = kst.pattern_match.group(1).lower()
    is_safety = any(_ in match for _ in ("-s", "safety"))
    try:
        if is_safety:
            await kst.client.edit_permissions(
                kst.chat_id,
                send_messages=True,
                send_media=False,
                send_stickers=False,
                send_gifs=False,
                send_games=False,
                send_inline=False,
                embed_link_previews=False,
                send_polls=False,
                change_info=False,
                invite_users=False,
                pin_messages=False,
            )
        else:
            await kst.client.edit_permissions(
                kst.chat_id,
                send_messages=True,
                change_info=False,
                pin_messages=False,
            )
        await kst.eor("`unlocked{}`".format(" safety" if is_safety else ""), time=5)
    except Exception as err:
        await kst.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="pin(?: |$)(.*)",
    require="pin_messages",
    func=lambda e: e.is_reply,
)
async def _(kst):
    match = kst.pattern_match.group(1).lower()
    is_notify = any(_ in match for _ in ("-n", "notify"))
    if kst.is_private:
        text = "Pinned!"
    else:
        link = (await kst.get_reply_message()).msg_link
        text = f"Pinned [This Message]({link}) !"
    try:
        await kst.client.pin_message(kst.chat_id, kst.reply_to_msg_id, notify=is_notify)
        await kst.eor(text)
    except Exception as err:
        await kst.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="tpin(?: |$)(.*)",
    require="pin_messages",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    opts = kst.pattern_match.group(1).lower().split(" ")
    sec = opts[0]
    if not (sec or sec.isdecimal()):
        return await kst.eor("`Provide a valid seconds!`", time=5)
    sec = int(sec)
    pinfor = time_formatter(sec * 1000)
    is_notify = any(_ in " ".join(opts[1:]).strip() for _ in ("-n", "notify"))
    msg_id = kst.reply_to_msg_id
    try:
        await ga.pin_message(chat_id, msg_id, notify=is_notify)
        await kst.eor(f"Pinned for {pinfor}.")
    except Exception as err:
        return await kst.eor(format_exc(err), parse_mode="html")
    await asyncio.sleep(sec)
    with suppress(BaseException):
        await ga.unpin_message(chat_id, msg_id)


@kasta_cmd(
    pattern="unpin$",
    require="pin_messages",
    func=lambda e: e.is_reply,
)
async def _(kst):
    try:
        await kst.client.unpin_message(kst.chat_id, kst.reply_to_msg_id)
        await kst.eor("`unpinned`", time=5)
    except Exception as err:
        await kst.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="unpinall$",
    require="add_admins",
)
async def _(kst):
    try:
        await kst.client.unpin_message(kst.chat_id, None)
        await kst.eor("`unpinned all`", time=5)
    except Exception as err:
        await kst.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="pinned$",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    chat = await kst.get_chat()
    if isinstance(chat, typ.Chat):
        where = await ga(fun.messages.GetFullChatRequest(chat.id))
    elif isinstance(chat, typ.Channel):
        where = await ga(fun.channels.GetFullChannelRequest(chat.id))
    else:
        return
    msg_id = where.full_chat.pinned_msg_id
    if not msg_id:
        return await yy.eor("`No Pinned!`", time=5)
    msg = await ga.get_messages(chat.id, ids=msg_id)
    if msg:
        await yy.eor("Pinned message [in here]({}).".format(msg.msg_link))


@kasta_cmd(
    pattern="listpinned$",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    yy = await kst.eor("`Processing...`")
    title = display_name(kst.chat)
    pinned = ""
    count = 1
    async for x in ga.iter_messages(chat_id, filter=typ.InputMessagesFilterPinned):
        if x.message:
            t = " ".join(x.message.split()[:4])
            btn = f"{t}...."
        else:
            btn = "Go to message..."
        pinned += f"{count}. <a href=https://t.me/c/{chat_id}/{x.id}>{btn}</a>\n"
        count += 1
    text = f"<b>Pinned message(s) in {normalize(title).lower()}:</b>\n"
    if not pinned:
        return await yy.eor("`No Pinned!`", time=5)
    await yy.eor(text + pinned, parts=True, parse_mode="html")


@kasta_cmd(
    pattern="promote(?: |$)(.*)",
    admins_only=True,
    require="add_admins",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Promoting...`")
    user, args = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot promote to myself.`", time=3)
    opts = args.split(" ")
    is_full = any(_ in opts[0].lower() for _ in ("-f", "full"))
    title = " ".join(strip_emoji(" ".join(opts[1:] if is_full else opts)).split()).strip()
    if len(title) > 16:
        title = title[:16]
    try:
        if is_full:
            await ga.edit_admin(
                chat_id,
                user.id,
                is_admin=True,
                title=title,
            )
        else:
            await ga.edit_admin(
                chat_id,
                user.id,
                change_info=False,
                post_messages=False,
                edit_messages=False,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=False,
                add_admins=False,
                manage_call=True,
                anonymous=False,
                title=title,
            )
        text = "{} is now admin with title {}".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            title,
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="demote(?: |$)(.*)",
    admins_only=True,
    require="add_admins",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Demoting...`")
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot demote to myself.`", time=3)
    try:
        await ga.edit_admin(
            chat_id,
            user.id,
            change_info=False,
            post_messages=False,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            manage_call=False,
            anonymous=False,
        )
        text = "{} is no longer admin.".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
        )
        await yy.eor(text, parse_mode="html")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="kickusers?(?: |$)(.*)",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Processing...`")
    user = (await ga.get_text(kst)).lower()
    total, kicked = 0, 0
    empty, month, week, offline, online, recently, bot, deleted, none = 0, 0, 0, 0, 0, 0, 0, 0, 0
    async for x in ga.iter_participants(chat_id):
        total += 1
        if isinstance(x.status, typ.UserStatusEmpty):
            if "empty" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                empty += 1
        if isinstance(x.status, typ.UserStatusLastMonth):
            if "month" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                month += 1
        if isinstance(x.status, typ.UserStatusLastWeek):
            if "week" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                week += 1
        if isinstance(x.status, typ.UserStatusOffline):
            if "offline" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                offline += 1
        if isinstance(x.status, typ.UserStatusOnline):
            if "online" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                online += 1
        if isinstance(x.status, typ.UserStatusRecently):
            if "recently" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                recently += 1
        if x.bot:
            if "bot" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                bot += 1
        elif x.deleted:
            if "deleted" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                deleted += 1
        elif x.status is None:
            if "none" in user:
                with suppress(BaseException):
                    await ga.kick_participant(chat_id, x.id)
                    kicked += 1
            else:
                none += 1
    if user:
        text = f"**Kicked {kicked} / {total} Users**\n"
    else:
        text = f"**Total {total} Users**\n"
    text += f"`{hl}kickusers deleted`  •  `{deleted}`\n"
    text += f"`{hl}kickusers empty`  •  `{empty}`\n"
    text += f"`{hl}kickusers month`  •  `{month}`\n"
    text += f"`{hl}kickusers week`  •  `{week}`\n"
    text += f"`{hl}kickusers offline`  •  `{offline}`\n"
    text += f"`{hl}kickusers online`  •  `{online}`\n"
    text += f"`{hl}kickusers recently`  •  `{recently}`\n"
    text += f"`{hl}kickusers bot`  •  `{bot}`\n"
    text += f"`{hl}kickusers none`  •  `{none}`"
    await yy.eor(text)


@kasta_cmd(
    pattern="kickdel$",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Kicking deleted accounts...`")
    try:
        done = [
            await ga.kick_participant(chat_id, x.id)
            for x in await ga.get_participants(chat_id)
            if not hasattr(x.participant, "admin_rights") and x.deleted
        ]
        await yy.eor(f"`Successfully kicked {len(done)} deleted account(s) in {normalize(kst.chat.title).lower()}.`")
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="unbanall$",
    admins_only=True,
    require="ban_users",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Unbanning all banned users...`")
    done = 0
    async for x in ga.iter_participants(
        chat_id,
        filter=typ.ChannelParticipantsKicked,
    ):
        try:
            await ga.edit_permissions(chat_id, x.id)
            await asyncio.sleep(0.5)
            done += 1
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds + 10)
            try:
                await ga.edit_permissions(chat_id, x.id)
                await asyncio.sleep(0.5)
                done += 1
            except BaseException:
                pass
        except BaseException:
            pass
    await yy.eor(f"`Successfully unbanned {done} users in {normalize(kst.chat.title).lower()}.`")


@kasta_cmd(
    pattern="adminlist$",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Processing...`")
    total = 0
    text = f"<b>Admins in {normalize(kst.chat.title).lower()}:</b>\n"
    async for x in ga.iter_participants(chat_id, filter=typ.ChannelParticipantsAdmins):
        if not (x.deleted or x.participant.admin_rights.anonymous):
            if isinstance(x.participant, typ.ChannelParticipantCreator):
                text += "- {} Owner\n".format(mentionuser(x.id, display_name(x), html=True))
            elif x.bot:
                text += "- {} Bot\n".format(mentionuser(x.id, display_name(x), html=True))
            elif x.is_self:
                text += "- {} Me\n".format(mentionuser(x.id, display_name(x), html=True))
            else:
                text += "- {}\n".format(mentionuser(x.id, display_name(x), html=True))
            total += 1
    text += f"\n<i>Found {total} admins without anonymously.</i>"
    await yy.eor(text, parts=True, parse_mode="html")


plugins_help["admintools"] = {
    "{i}ban [reply]/[username/mention/id] [reason]": "Ban user and report them as spam.",
    "{i}dban [reply] [reason]": "Ban user by reply, delete their message and report them as spam.",
    "{i}sban [reply]/[username/mention/id]": "Silently a ban user, delete my message and report them as spam.",
    "{i}tban [reply]/[username/mention/id] [timing] [reason]": "Temporarily ban user. **timing:** 4m = 4 minutes, 3h = 3 hours, 6d = 6 days.",
    "{i}unban [reply]/[username/mention/id] [reason]": "Unbanned user.",
    "{i}mute [reply]/[username/mention/id] [reason]": "Mute user.",
    "{i}dmute [reply] [reason]": "Mute user by reply, and delete their message.",
    "{i}smute [reply]/[username/mention/id]": "Silently mute user, and delete my message.",
    "{i}tmute [reply]/[username/mention/id] [timing] [reason]": "Temporarily mute user. **timing:** 4m = 4 minutes, 3h = 3 hours, 6d = 6 days.",
    "{i}unmute [reply]/[username/mention/id] [reason]": "Unmute user.",
    "{i}kick [reply]/[username/mention/id] [reason]": "Kick user.",
    "{i}dkick [reply] [reason]": "Kick user by reply, and delete their message.",
    "{i}skick [reply]/[username/mention/id]": "Silently a kick user, and delete my message.",
    "{i}lock": "Lock current group, allowing read only for non-admins.",
    "{i}unlock [-s/safety]": "Unlock current group, allowing read/write for non-admins (excludes: change_info, pin_messages). Add '-s' to allowing just for typing.",
    "{i}pin [reply] [-n/notify]": "Pin the replied message. Add '-n' to send a notification.",
    "{i}tpin [reply] [seconds] [-n/notify]": "Temporarily pin the replied message. Add '-n' to send a notification.",
    "{i}unpin [reply]": "Unpin the replied message.",
    "{i}unpinall": "Unpins all pinned messages.",
    "{i}pinned": "Get the current pinned message.",
    "{i}listpinned": "Get all pinned messages.",
    "{i}promote [reply]/[username/mention/id] [-f/full] [title]": "Promote user as admin. To full permissions add '-f'. The title must be less than 16 characters and emoji are not allowed, or use the default localized title.",
    "{i}demote [reply]/[username/mention/id]": "Demote user from admin.",
    "{i}kickusers": "Kick users specifically.",
    "{i}kickdel": "Kick all deleted accounts.",
    "{i}unbanall": "Unban all banned users.",
    "{i}adminlist": """Get list all admins by type in current group.

**Examples:**
- Mute user for two hours.
-> `{i}tmute @username 2h abuse`

- Promote user as co-founder with blank title.
-> `{i}promote @username -f ㅤ`
""",
}
