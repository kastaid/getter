# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from asyncio import sleep
from telethon.tl.custom import Message
from telethon.tl.types import MessageService


async def eor(e, text=None, **args):
    time = args.get("time", None)
    edit_time = args.get("edit_time", None)
    force_reply = args.get("force_reply", False)
    if len(text) > 4096:
        args["parse_mode"] = "markdown"
        text = "`Text too long or large size.`"
    if "time" in args:
        del args["time"]
    if "edit_time" in args:
        del args["edit_time"]
    if "force_reply" in args:
        del args["force_reply"]
    if "link_preview" not in args:
        args.update({"link_preview": False})
    if hasattr(e, "out") and e.out and not isinstance(e, MessageService):
        if "silent" in args:
            del args["silent"]
        if edit_time:
            await sleep(edit_time)
        try:
            try:
                del args["reply_to"]
            except KeyError:
                pass
            res = await e.edit(text, **args)
        except BaseException:
            return
    else:
        _ = e if force_reply else None
        args["reply_to"] = e.reply_to_msg_id or _
        res = await e.client.send_message(e.chat_id, text, **args)
    if time:
        await sleep(time)
        return await _try_delete(res)
    return res


async def eod(e, text=None, **kwargs):
    kwargs["time"] = kwargs.get("time", 8)
    return await eor(e, text, **kwargs)


async def eos(e, text=None, **args):
    edit = args.get("edit", False)
    force_reply = args.get("force_reply", False)
    if len(text) > 4096:
        args["parse_mode"] = "markdown"
        text = "`Text too long or large size.`"
    if "edit" in args:
        del args["edit"]
    if "force_reply" in args:
        del args["force_reply"]
    if "link_preview" not in args:
        args.update({"link_preview": False})
    if "silent" not in args:
        args.update({"silent": True})
    if edit:
        if "silent" in args:
            del args["silent"]
        try:
            try:
                del args["reply_to"]
            except KeyError:
                pass
            await e.edit(text, **args)
        except BaseException:
            return
    else:
        _ = e if force_reply else None
        args["reply_to"] = e.reply_to_msg_id or _
        await _try_delete(e)
        await e.client.send_message(e.chat_id, text, **args)


async def _try_delete(e):
    try:
        return await e.delete()
    except BaseException:
        pass


setattr(Message, "eor", eor)  # noqa: B010
setattr(Message, "eod", eod)  # noqa: B010
setattr(Message, "eos", eos)  # noqa: B010
setattr(Message, "try_delete", _try_delete)  # noqa: B010
