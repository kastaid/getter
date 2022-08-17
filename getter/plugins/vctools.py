# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from contextlib import suppress
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import GetFullChannelRequest, DeleteMessagesRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.phone import CreateGroupCallRequest, DiscardGroupCallRequest, EditGroupCallTitleRequest
from . import HELP, kasta_cmd, CALLS


async def get_call(e, chat_id):
    try:
        call = await e.client(GetFullChannelRequest(channel=chat_id))
        return call.full_chat.call
    except FloodWaitError:
        return None


async def get_chat_id(e):
    target = e.pattern_match.group(1)
    chat_id = None
    if not target:
        return int(str(e.chat_id).replace("-100", ""))
    if str(target).isdecimal() or (str(target).startswith("-") and str(target)[1:].isdecimal()):
        if str(target).startswith("-100"):
            chat_id = int(str(target).replace("-100", ""))
        elif str(target).startswith("-"):
            chat_id = int(str(target).replace("-", ""))
        else:
            chat_id = int(target)
    else:
        try:
            req = await e.client(GetFullChatRequest(chat_id=target))
            chat_id = req.full_chat.id
        except BaseException:
            try:
                req = await e.client(GetFullChannelRequest(channel=target))
                chat_id = req.full_chat.id
            except Exception as err:
                return await e.eor(f"```{err}```")
    return chat_id


@kasta_cmd(
    pattern="startvc(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    opts = kst.pattern_match.group(1)
    args = opts.split(" ")
    silent = True if args[0] in ("s", "silent") else False
    title = ""
    for x in args[1:]:
        title += x + " "
    req = await kst.client(
        CreateGroupCallRequest(
            peer=kst.chat_id,
            title=title,
        )
    )
    if not silent:
        await msg.eor("__Starting a video chat...__", time=5)
        return
    else:
        await msg.try_delete()
        if req and req.updates[1].id is not None:
            await kst.client(DeleteMessagesRequest(kst.chat_id, [req.updates[1].id]))


@kasta_cmd(
    pattern="stopvc(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    opts = kst.pattern_match.group(1)
    silent = True if opts in ("s", "silent") else False
    try:
        call = await get_call(kst, kst.chat_id)
    except BaseException:
        call = None
    if not call:
        await msg.eor("__No video chat.__", time=5)
        return
    req = await kst.client(DiscardGroupCallRequest(call=call))
    if not silent:
        await msg.eor("__Stopping video chat...__", time=5)
        return
    else:
        await msg.try_delete()
        if req and req.updates[1].id is not None:
            await kst.client(DeleteMessagesRequest(kst.chat_id, [req.updates[1].id]))


@kasta_cmd(
    pattern="joinvc(?: |$)(.*)",
)
async def _(kst):
    try:
        import pytgcalls
    except ImportError:
        return
    chat_id = await get_chat_id(kst)
    msg = await kst.eor("`Processing...`")
    try:
        call = await get_call(kst, chat_id)
    except BaseException:
        call = None
    if not call:
        await msg.eor("__No video chat.__", time=5)
        return
    group_call = CALLS.get(chat_id)
    if group_call is None:
        group_call = pytgcalls.GroupCallFactory(
            kst.client,
            pytgcalls.GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON,
            enable_logs_to_console=False,
            path_to_log_file=None,
        ).get_file_group_call(None)
        CALLS[chat_id] = group_call
    if not (group_call and group_call.is_connected):
        with suppress(BaseException):
            await group_call.start(chat_id, enable_action=False)
        await asyncio.sleep(2)
        with suppress(BaseException):
            await group_call.set_is_mute(True)
        with suppress(BaseException):
            await group_call.edit_group_call(muted=True)
    await msg.eor("`joined`", time=5)


@kasta_cmd(
    pattern="leavevc(?: |$)(.*)",
)
async def _(kst):
    chat_id = await get_chat_id(kst)
    msg = await kst.eor("`Processing...`")
    try:
        call = await get_call(kst, chat_id)
    except BaseException:
        call = None
    if not call:
        await msg.eor("__No video chat.__", time=5)
        return
    group_call = CALLS.get(chat_id)
    if group_call and group_call.is_connected:
        with suppress(BaseException):
            await group_call.stop()
        CALLS.pop(chat_id, None)
    await msg.eor("`leaved`", time=5)


@kasta_cmd(
    pattern="vctitle(?: |$)(.*)",
    admins_only=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    title = kst.pattern_match.group(1)
    if not title:
        return msg.eor("__Required some text for title.__", time=5)
    try:
        call = await get_call(kst, kst.chat_id)
    except BaseException:
        call = None
    if not call:
        await msg.eor("__No video chat.__", time=5)
        return
    await kst.client(EditGroupCallTitleRequest(call=call, title=title.strip()))
    await msg.eor("`changed`", time=5)


HELP.update(
    {
        "vctools": [
            "Video Chats Tools",
            """❯ `{i}startvc <silent/s> <title>`
Start a video chat.

❯ `{i}stopvc <silent/s>`
Stop the video chat.

❯ `{i}joinvc <chat_id/username group/channel>`
Join the video chat.

❯ `{i}leavevc <chat_id/username group/channel>`
Leave the video chat.

❯ `{i}vctitle <title>`
Change the video chat title.
""",
        ]
    }
)
