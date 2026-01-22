# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from random import choice

from telethon.errors import UserAlreadyParticipantError
from telethon.tl import functions as fun

from . import (
    CALLS,
    display_name,
    getter_app,
    humanbool,
    import_lib,
    is_termux,
    kasta_cmd,
    mentionuser,
    normalize_chat_id,
    plugins_help,
)


@kasta_cmd(
    pattern="startvc(?: |$)(.*)",
    admins_only=True,
    require="manage_call",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Starting video chat...`")
    args = kst.pattern_match.group(1).split(" ")
    is_silent = any(_ in args[0].lower() for _ in ("-s", "silent"))
    title = " ".join(args[1:] if is_silent else args).strip()
    chat_id = normalize_chat_id(kst.chat_id)
    call = await get_call(chat_id)
    if call:
        return await yy.eor("`Video chat is available.`", time=5)
    try:
        res = await ga(
            fun.phone.CreateGroupCallRequest(
                chat_id,
                title=title,
            )
        )
    except BaseException:
        return await yy.eor("`An error occurred. Try again now!`", time=5)
    if CALLS.get(chat_id):
        CALLS.pop(chat_id, None)
    if not is_silent:
        return await yy.eor("`Video chat started.`", time=5)
    await yy.try_delete()
    if res:
        ids = [_.id for _ in res.updates if hasattr(_, "id")]
        if ids:
            await ga.delete_messages(chat_id, ids)


@kasta_cmd(
    pattern="stopvc(?: |$)(.*)",
    admins_only=True,
    require="manage_call",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Stopping video chat...`")
    args = kst.pattern_match.group(1).split(" ")
    is_silent = any(_ in args[0].lower() for _ in ("-s", "silent"))
    chat_id = normalize_chat_id(kst.chat_id)
    call = await get_call(chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    try:
        res = await ga(fun.phone.DiscardGroupCallRequest(call))
    except BaseException:
        return await yy.eor("`An error occurred. Try again now!`", time=5)
    if CALLS.get(chat_id):
        CALLS.pop(chat_id, None)
    if not is_silent:
        return await yy.eor("`Video chat stopped.`", time=5)
    await yy.try_delete()
    if res:
        ids = [_.id for _ in res.updates if hasattr(_, "id")]
        if ids:
            await ga.delete_messages(chat_id, ids)


@kasta_cmd(
    pattern="vctitle(?: |$)(.*)",
    admins_only=True,
    require="manage_call",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    title = await ga.get_text(kst)
    chat_id = normalize_chat_id(kst.chat_id)
    call = await get_call(chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    try:
        await ga(fun.phone.EditGroupCallTitleRequest(call, title=title))
        await yy.eor("`Video chat title changed.`", time=5)
    except BaseException:
        await yy.eor("`Unchanged video chat title!`", time=5)


@kasta_cmd(
    pattern="invitevc(?: |$)(.*)",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Inviting to video chat...`")
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot invite to myself.`", time=3)
    chat_id = normalize_chat_id(kst.chat_id)
    call = await get_call(chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    try:
        await ga(fun.phone.InviteToGroupCallRequest(call, users=[user.id]))
        text = "`Invited to video chat.`"
    except UserAlreadyParticipantError:
        text = "`User is already invited.`"
    except BaseException:
        text = "`Cannot invite a user!`"
    await yy.eor(text, time=5)


"""
@kasta_cmd(
    pattern="vcinviteall$",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Inviting members to video chat...`")
    call = await get_call(kst.chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    users, done = [], 0
    async for x in ga.iter_participants(entity=kst.chat_id, limit=None):
        if not (
            x.deleted
            or x.bot
            or x.is_self
            or (hasattr(x.participant, "admin_rights") and x.participant.admin_rights.anonymous)
        ) and get_user_status(x) != "long_time_ago":
            users.append(x.id)
    for user in chunk(users, 6):
        try:
            await ga(InviteToGroupCallRequest(call, users=user))
            done += 6
        except FloodWaitError as fw:
            # from telethon.errors import FloodWaitError
            flood = fw.seconds
            await yy.eor("`Inviting wait in {}...`".format(time_formatter((flood + 5) * 1000)))
            await asyncio.sleep(flood + 5)
            await ga(InviteToGroupCallRequest(call=call, users=user))
            done += 6
        except BaseException:
            pass
    await yy.eod(f"`Invited {done} users.`")
"""


@kasta_cmd(
    pattern="vcinfos?$",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    chat_id = normalize_chat_id(kst.chat_id)
    call = await get_call(chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    try:
        res = await ga(fun.phone.GetGroupCallRequest(call, limit=1))
    except BaseException:
        return await yy.eor("`An error occurred. Try again now!`", time=5)
    text = "<b><u>Video Chat Information</u></b>\n"
    text += f"<b>Title:</b> <code>{res.call.title or ''}</code>\n"
    text += f"<b>Join Muted:</b> <code>{humanbool(res.call.join_muted)}</code>\n"
    text += f"<b>Participants Count:</b> <code>{res.call.participants_count}</code>\n\n"
    if res.call.participants_count > 0:
        text += "<b><u>Participants</u></b>\n"
        for x in res.users:
            mention = mentionuser(x.id, display_name(x), html=True, width=15)
            text += f"• <code>{x.id}</code> – {mention}\n"
    await yy.eor(text, parts=True, parse_mode="html")


@kasta_cmd(
    pattern="joinvc(?: |$)(.*)",
)
@kasta_cmd(
    pattern="joinvc(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gjoinvc(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Joining video chat...`")
    chat_id = await ga.get_chat_id(kst)
    if not chat_id:
        return await yy.try_delete()
    call = await get_call(chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    in_call = group_call(chat_id)
    if not (in_call and in_call.is_connected):
        try:
            await in_call.start(chat_id, enable_action=False)
            text = "`Joined video chat.`"
            try:
                await asyncio.sleep(3)
                await in_call.set_is_mute(is_muted=True)
            except BaseException:
                pass
        except BaseException:
            if is_termux():
                text = "`This command doesn't not supported Termux. Use proot-distro instantly!`"
            else:
                text = "`Cannot join video chat!`"
    else:
        text = "`Already joined video chat!`"
    await yy.eor(text, time=5)


@kasta_cmd(
    pattern="leavevc(?: |$)(.*)",
)
@kasta_cmd(
    pattern="leavevc(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gleavevc(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Leaving video chat...`")
    chat_id = await ga.get_chat_id(kst)
    if not chat_id:
        return await yy.try_delete()
    call = await get_call(chat_id)
    if not call:
        return await yy.eor("`No video chat!`", time=5)
    in_call = group_call(chat_id)
    if in_call and in_call.is_connected:
        try:
            await in_call.stop()
        except BaseException:
            pass
        text = "`Leaved video chat.`"
    else:
        text = "`Not joined video chat!`"
    CALLS.pop(chat_id, None)
    await yy.eor(text, time=5)


@kasta_cmd(
    pattern="listvc$",
)
async def _(kst):
    if len(CALLS) > 0:
        text = f"<b><u>{len(CALLS)} Video Chats</u></b>\n"
        for x in CALLS:
            text += f"<code>-100{x}</code>\n"
        return await kst.eor(text, parts=True, parse_mode="html")
    text = "`You got no joined video chat!`"
    await kst.eor(text, time=5)


async def get_call(chat_id: int):
    try:
        call = await getter_app(fun.channels.GetFullChannelRequest(chat_id))
        return call.full_chat.call
    except BaseException:
        return None


def group_call_instance(chat_id: int) -> None:
    try:
        import pytgcalls
    except ImportError:
        if is_termux():
            return
        pytgcalls = import_lib(
            lib_name="pytgcalls",
            pkg_name="pytgcalls==3.0.0.dev24",
        )
    try:
        if chat_id not in CALLS:
            CALLS[chat_id] = pytgcalls.GroupCallFactory(
                getter_app,
                pytgcalls.GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON,
                enable_logs_to_console=False,
                path_to_log_file="",
            ).get_file_group_call(
                input_filename="",
                play_on_repeat=False,
            )
        call = CALLS.get(chat_id)

        @call.on_network_status_changed
        async def __(context, is_connected):  # noqa: RUF029
            if not is_connected:
                CALLS.pop(chat_id, None)

    except BaseException:
        pass


def group_call(chat_id: int):
    group_call_instance(chat_id)
    return CALLS.get(chat_id)


plugins_help["vctools"] = {
    "{i}startvc [-s/silent] [title]": "Start or restart the video chat in current group/channel. Add '-s' to started silently.",
    "{i}stopvc [-s/silent]": "Stop the video chat in current group/channel. Add '-s' to stopped silently.",
    "{i}vctitle [title]/[reply]": "Change the video chat title or reset to default (without title) in current group/channel.",
    "{i}invitevc [reply]/[username/mention/id]": "Invite user to current video chat.",
    # "{i}vcinviteall": "Invite all members to current video chat. **(YOU MUST BE JOINED)**",
    "{i}vcinfo": "Get information of current video chat.",
    "{i}joinvc [current/chat_id/username]/[reply]": "Join the video chat in group/channel.",
    "{i}leavevc [current/chat_id/username]/[reply]": "Leave the video chat in group/channel.",
    "{i}listvc": "List all joined video chats.",
}
