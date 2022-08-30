# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.phone import CreateGroupCallRequest, DiscardGroupCallRequest, EditGroupCallTitleRequest
from . import (
    getter_app,
    kasta_cmd,
    plugins_help,
    suppress,
    get_chat_id,
)

CALLS = {}

try:
    import pytgcalls

    group_call = pytgcalls.GroupCallFactory(
        getter_app,
        pytgcalls.GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON,
        enable_logs_to_console=False,
        path_to_log_file=None,
    ).get_file_group_call(input_filename="", play_on_repeat=False)

    @group_call.on_network_status_changed
    async def __(context, is_connected):
        if not is_connected:
            CALLS.pop(context.full_chat.id, None)

except ImportError:
    group_call = None


@kasta_cmd(
    pattern="startvc(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    chat_id = await get_chat_id(kst)
    yy = await kst.eor("`Processing...`")
    opts = kst.pattern_match.group(1)
    args = opts.split(" ")
    silent = True if args[0] in ("s", "silent") else False
    title = ""
    for x in args[1:]:
        title += x + " "
    req = await kst.client(
        CreateGroupCallRequest(
            peer=chat_id,
            title=title,
        )
    )
    if CALLS.get(chat_id):
        CALLS.pop(chat_id, None)
    if not silent:
        await yy.eor("__Starting a video chat...__", time=5)
        return
    await yy.try_delete()
    if req:
        reqs = [x.id for x in req.updates if hasattr(x, "id")]
        if reqs:
            await kst.client.delete_messages(chat_id, reqs)


@kasta_cmd(
    pattern="stopvc(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    chat_id = await get_chat_id(kst)
    yy = await kst.eor("`Processing...`")
    opts = kst.pattern_match.group(1)
    silent = True if opts in ("s", "silent") else False
    try:
        call = await get_call(kst, chat_id)
    except BaseException:
        call = None
    if not call:
        await yy.eor("__No video chat.__", time=5)
        return
    req = await kst.client(DiscardGroupCallRequest(call=call))
    if CALLS.get(chat_id):
        CALLS.pop(chat_id, None)
    if not silent:
        await yy.eor("__Stopping video chat...__", time=5)
        return
    await yy.try_delete()
    if req:
        reqs = [x.id for x in req.updates if hasattr(x, "id")]
        if reqs:
            await kst.client.delete_messages(chat_id, reqs)


@kasta_cmd(
    pattern="joinvc(?: |$)(.*)",
)
async def _(kst):
    if not group_call:
        return
    chat_id = await get_chat_id(kst)
    yy = await kst.eor("`Processing...`")
    try:
        call = await get_call(kst, chat_id)
    except BaseException:
        call = None
    if not call:
        await yy.eor("__No video chat.__", time=5)
        return
    if not CALLS.get(chat_id):
        CALLS[chat_id] = group_call
    in_call = CALLS.get(chat_id)
    if not (in_call and in_call.is_connected):
        with suppress(BaseException):
            await in_call.start(chat_id, enable_action=False)
        # await in_call.edit_group_call(volume=100, muted=True)
        await yy.eor("`joined`", time=5)
    else:
        with suppress(BaseException):
            await in_call.reconnect()
        await yy.eor("`rejoin`", time=5)
    await asyncio.sleep(3)


@kasta_cmd(
    pattern="leavevc(?: |$)(.*)",
)
async def _(kst):
    chat_id = await get_chat_id(kst)
    yy = await kst.eor("`Processing...`")
    try:
        call = await get_call(kst, chat_id)
    except BaseException:
        call = None
    if not call:
        await yy.eor("__No video chat.__", time=5)
        return
    in_call = CALLS.get(chat_id)
    if in_call and in_call.is_connected:
        with suppress(BaseException):
            await in_call.stop()
        CALLS.pop(chat_id, None)
    await yy.eor("`leaved`", time=5)
    await asyncio.sleep(3)


@kasta_cmd(
    pattern="vctitle(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    title = kst.pattern_match.group(1)
    if not title:
        await yy.eor("__Required some text for title.__", time=5)
        return
    try:
        call = await get_call(kst, kst.chat_id)
    except BaseException:
        call = None
    if not call:
        await yy.eor("__No video chat.__", time=5)
        return
    with suppress(BaseException):
        await kst.client(EditGroupCallTitleRequest(call=call, title=title.strip()))
    await yy.eor("`changed`", time=5)
    await asyncio.sleep(3)


"""
@kasta_cmd(
    pattern="vcinvite$",
    groups_only=True,
)
async def _(kst):
    yy = await kst.eor("`Inviting members to video chat...`")
    try:
        call = await get_call(kst, kst.chat_id)
    except BaseException:
        call = None
    if not call:
        await yy.eor("__No video chat.__", time=5)
        return
    users = []
    done = 0
    async for x in kst.client.iter_participants(kst.chat_id):
        if not (
            x.deleted
            or x.bot
            or x.is_self
            or (hasattr(x.participant, "admin_rights") and x.participant.admin_rights.anonymous)
        ) and get_user_status(x) != "long_time_ago":
            users.append(x.id)
    for user in chunk(users, 6):
        try:
            await kst.client(InviteToGroupCallRequest(call=call, users=user))
            done += 6
        except FloodWaitError as fw:
            flood = fw.seconds
            await yy.eor("`Inviting wait in {}...`".format(time_formatter((flood + 5) * 1000)))
            await asyncio.sleep(flood + 5)
            await kst.client(InviteToGroupCallRequest(call=call, users=user))
            done += 6
        except BaseException:
            pass
    await yy.eod("`invited {}`".format(done))
"""


async def get_call(kst, chat_id):
    try:
        call = await kst.client(GetFullChannelRequest(channel=chat_id))
        return call.full_chat.call
    except FloodWaitError:
        return None


plugins_help["vctools"] = {
    "{i}startvc [silent/s] [title]": "Start a video chat.",
    "{i}stopvc [silent/s]": "Stop the video chat.",
    "{i}joinvc [chat_id/username group/channel]": "Join the video chat.",
    "{i}leavevc [chat_id/username group/channel]": "Leave the video chat.",
    "{i}vctitle [title]": "Change the video chat title.",
    # "{i}vcinvite": "Invite all members to current video chat. **(YOU MUST BE JOINED)**",
}
