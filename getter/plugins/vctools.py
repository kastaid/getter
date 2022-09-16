# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from telethon.tl import functions as fun
from . import (
    CALLS,
    getter_app,
    kasta_cmd,
    plugins_help,
    suppress,
    normalize_chat_id,
    get_chat_id,
    is_termux,
    import_lib,
)


@kasta_cmd(
    pattern="startvc(?: |$)(.*)",
    admins_only=True,
    require="manage_call",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    yy = await kst.eor("`Starting video chat...`")
    args = kst.pattern_match.group(1).split(" ")
    is_silent = "-s" in args[0].lower()
    title = " ".join(args[1:] if is_silent else args).strip()
    try:
        req = await ga(
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
        await yy.eor("`Video chat started.`", time=5)
        return
    await yy.try_delete()
    if req:
        reqs = [_.id for _ in req.updates if hasattr(_, "id")]
        if reqs:
            await ga.delete_messages(chat_id, reqs)


@kasta_cmd(
    pattern="stopvc(?: |$)(.*)",
    admins_only=True,
    require="manage_call",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    yy = await kst.eor("`Stopping video chat...`")
    args = kst.pattern_match.group(1).split(" ")
    is_silent = "-s" in args[0].lower()
    call = await get_call(kst, chat_id)
    if not call:
        await yy.eor("`No video chat!`", time=5)
        return
    try:
        req = await ga(fun.phone.DiscardGroupCallRequest(call))
    except BaseException:
        return await yy.eor("`An error occurred. Try again now!`", time=5)
    if CALLS.get(chat_id):
        CALLS.pop(chat_id, None)
    if not is_silent:
        await yy.eor("`Video chat stopped.`", time=5)
        return
    await yy.try_delete()
    if req:
        reqs = [_.id for _ in req.updates if hasattr(_, "id")]
        if reqs:
            await ga.delete_messages(chat_id, reqs)


@kasta_cmd(
    pattern="joinvc(?: |$)(.*)",
)
async def _(kst):
    chat_id = await get_chat_id(kst)
    if not chat_id:
        return await kst.try_delete()
    yy = await kst.eor("`Joining video chat...`")
    call = await get_call(kst, chat_id)
    if not call:
        await yy.eor("`No video chat!`", time=5)
        return
    in_call = group_call(chat_id)
    if not (in_call and in_call.is_connected):
        try:
            await in_call.start(chat_id, enable_action=False)
            text = "`Joined video chat.`"
            with suppress(BaseException):
                await asyncio.sleep(3)
                await in_call.edit_group_call(muted=True)
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
async def _(kst):
    chat_id = await get_chat_id(kst)
    if not chat_id:
        return await kst.try_delete()
    yy = await kst.eor("`Leaving video chat...`")
    call = await get_call(kst, chat_id)
    if not call:
        await yy.eor("`No video chat!`", time=5)
        return
    in_call = group_call(chat_id)
    if in_call and in_call.is_connected:
        with suppress(BaseException):
            await in_call.stop()
        CALLS.pop(chat_id, None)
        text = "`Leaved video chat.`"
    else:
        text = "`Not joined video chat!`"
    await yy.eor(text, time=5)


@kasta_cmd(
    pattern="vctitle(?: |$)(.*)",
    admins_only=True,
    require="manage_call",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    yy = await kst.eor("`Processing...`")
    title = await ga.get_text(kst)
    call = await get_call(kst, chat_id)
    if not call:
        await yy.eor("`No video chat!`", time=5)
        return
    try:
        await ga(fun.phone.EditGroupCallTitleRequest(call, title=title))
        await yy.eor("`Video chat title changed.`", time=5)
    except BaseException:
        await yy.eor("`Unchanged video chat title!`", time=5)


@kasta_cmd(
    pattern="listvc$",
)
async def _(kst):
    if len(CALLS) > 0:
        text = f"<b><u>{len(CALLS)} Video Chats</u></b>\n"
        for x in CALLS:
            text += f"<code>-100{x}</code>\n"
        return await kst.eor(text, parse_mode="html")
    text = "`You got no joined video chat!`"
    await kst.eor(text, time=5)


"""
@kasta_cmd(
    pattern="vcinvite$",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Inviting members to video chat...`")
    call = await get_call(kst, kst.chat_id)
    if not call:
        await yy.eor("`No video chat!`", time=5)
        return
    users, done = [], 0
    async for x in ga.iter_participants(kst.chat_id):
        if not (
            x.deleted
            or x.bot
            or x.is_self
            or (hasattr(x.participant, "admin_rights") and x.participant.admin_rights.anonymous)
        ) and get_user_status(x) != "long_time_ago":
            users.append(x.id)
    for user in chunk(users, 6):
        try:
            await ga(InviteToGroupCallRequest(call=call, users=user))
            done += 6
        except FloodWaitError as fw:
            # from telethon.errors.rpcerrorlist import FloodWaitError
            flood = fw.seconds
            await yy.eor("`Inviting wait in {}...`".format(time_formatter((flood + 5) * 1000)))
            await asyncio.sleep(flood + 5)
            await ga(InviteToGroupCallRequest(call=call, users=user))
            done += 6
        except BaseException:
            pass
    await yy.eod(f"`Invited {done} users.`")
"""


async def get_call(kst, chat_id):
    try:
        call = await kst.client(fun.channels.GetFullChannelRequest(chat_id))
        return call.full_chat.call
    except BaseException:
        return None


def group_call_instance(chat_id: int):
    try:
        import pytgcalls
    except ImportError:
        if is_termux():
            return
        pytgcalls = import_lib("pytgcalls==3.0.0.dev22")
    if chat_id not in CALLS:
        CALLS[chat_id] = pytgcalls.GroupCallFactory(
            getter_app,
            pytgcalls.GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON,
            enable_logs_to_console=False,
            path_to_log_file=None,
        ).get_file_group_call(
            input_filename="",
            play_on_repeat=False,
        )
    call = CALLS.get(chat_id)

    @call.on_network_status_changed
    async def __(context, is_connected):
        if not is_connected:
            CALLS.pop(chat_id, None)


def group_call(chat_id: int):
    group_call_instance(chat_id)
    return CALLS.get(chat_id)


plugins_help["vctools"] = {
    "{i}startvc [-s] [title]": "Start or restart the video chat in current group/channel. Add '-s' to started silently.",
    "{i}stopvc [-s]": "Stop the video chat in current group/channel. Add '-s' to stopped silently.",
    "{i}joinvc [current/chat_id/username]/[reply]": "Join the video chat in group/channel.",
    "{i}leavevc [current/chat_id/username]/[reply]": "Leave the video chat in group/channel.",
    "{i}vctitle [title]/[reply]": "Change the video chat title or reset to default (without title) in current group/channel.",
    "{i}listvc": "List all joined video chats.",
    # "{i}vcinvite": "Invite all members to current video chat. **(YOU MUST BE JOINED)**",
}
