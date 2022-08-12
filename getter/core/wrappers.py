# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from asyncio import sleep
from contextlib import suppress
from aiofiles import open as aiopen
from telethon.tl.types import MessageService
from getter import Root, MAX_MESSAGE_LEN
from getter.core.functions import strip_format


async def eor(e, text=None, **args):
    time = args.get("time", None)
    edit_time = args.get("edit_time", None)
    force_reply = args.get("force_reply", False)
    args["reply_to"] = e.reply_to_msg_id or (e if force_reply else None)
    if len(text) > MAX_MESSAGE_LEN:
        text = strip_format(text)
        file = "message_output.txt"
        async with aiopen(file, mode="w") as f:
            await f.write(text)
        with suppress(BaseException):
            chat = await e.get_chat()
            await e.client.send_file(
                chat,
                file=file,
                caption=r"\\**#Getter**// `Message Too Long`",
                force_document=True,
                allow_cache=False,
                reply_to=args["reply_to"],
                silent=True,
            )
        await _try_delete(e)
        return (Root / file).unlink(missing_ok=True)
    if "time" in args:
        del args["time"]
    if "edit_time" in args:
        del args["edit_time"]
    if "force_reply" in args:
        del args["force_reply"]
    if "link_preview" not in args:
        args.update({"link_preview": False})
    if e.out and not isinstance(e, MessageService):
        if "silent" in args:
            del args["silent"]
        if "reply_to" in args:
            del args["reply_to"]
        if edit_time:
            await sleep(edit_time)
        try:
            res = await e.edit(text, **args)
        except BaseException:
            return
    else:
        res = await e.client.send_message(e.chat_id, text, **args)
    if time:
        await sleep(time)
        return await _try_delete(res)
    return res


async def eod(e, text=None, **kwargs):
    kwargs["time"] = kwargs.get("time", 8)
    return await eor(e, text, **kwargs)


async def sod(e, text=None, **args):
    delete = args.get("delete", True)
    time = args.get("time", None)
    force_reply = args.get("force_reply", False)
    args["reply_to"] = e.reply_to_msg_id or (e if force_reply else None)
    if delete:
        await _try_delete(e)
    if len(text) > MAX_MESSAGE_LEN:
        text = strip_format(text)
        file = "message_output.txt"
        async with aiopen(file, mode="w") as f:
            await f.write(text)
        with suppress(BaseException):
            await e.client.send_file(
                e.chat_id,
                file=file,
                caption=r"\\**#Getter**// `Message Too Long`",
                force_document=True,
                allow_cache=False,
                reply_to=args["reply_to"],
                silent=True,
            )
        await _try_delete(e)
        return (Root / file).unlink(missing_ok=True)
    if "delete" in args:
        del args["delete"]
    if "time" in args:
        del args["time"]
    if "force_reply" in args:
        del args["force_reply"]
    if "link_preview" not in args:
        args.update({"link_preview": False})
    if "silent" not in args:
        args.update({"silent": True})
    res = await e.client.send_message(e.chat_id, text, **args)
    if time:
        await sleep(time)
        return await _try_delete(res)
    return res


async def _try_delete(e):
    with suppress(BaseException):
        return await e.delete()
