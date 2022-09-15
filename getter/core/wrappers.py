# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from contextlib import suppress
from io import BytesIO
from telethon.errors.rpcerrorlist import MessageIdInvalidError, MessageNotModifiedError
from telethon.tl.types import MessageService
from ..config import MAX_MESSAGE_LEN
from .utils import strip_format


async def eor(
    kst,
    text=None,
    link_preview=False,
    silent=False,
    time=None,
    edit_time=None,
    force_reply=False,
    **args,
):
    _ = args.get("reply_to", None)
    reply_to = _ if _ else (kst.reply_to_msg_id or (kst if force_reply else None))
    for arg in (
        "entity",
        "message",
        "text",
        "link_preview",
        "silent",
        "reply_to",
    ):
        if arg in args:
            del args[arg]
    if len(text) > MAX_MESSAGE_LEN:
        with suppress(BaseException), BytesIO(str.encode(strip_format(text))) as file:
            file.name = "message.txt"
            await kst.respond(
                r"\\**#Getter**// Message Too Long",
                file=file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to,
                silent=True,
            )
        return await try_delete(kst)
    if kst.out and not isinstance(kst, MessageService):
        if edit_time:
            await asyncio.sleep(edit_time)
        try:
            yy = await kst.edit(
                text,
                link_preview=link_preview,
                **args,
            )
        except MessageIdInvalidError:  # keep functions running
            return
        except MessageNotModifiedError:
            yy = kst
    else:
        with suppress(BaseException):
            yy = await kst.respond(
                message=text,
                link_preview=link_preview,
                silent=silent,
                reply_to=reply_to,
                **args,
            )
    if time:
        await asyncio.sleep(time)
        return await try_delete(yy)
    return yy


async def eod(kst, text=None, **kwargs):
    kwargs["time"] = kwargs.get("time", 8)
    return await eor(kst, text, **kwargs)


async def sod(
    kst,
    text=None,
    chat_id=None,
    link_preview=False,
    silent=False,
    time=None,
    edit_time=None,
    force_reply=False,
    delete=True,
    **args,
):
    chat_id = chat_id or kst.chat_id
    _ = args.get("reply_to", None)
    reply_to = _ if _ else (kst.reply_to_msg_id or (kst if force_reply else None))
    for arg in (
        "entity",
        "message",
        "link_preview",
        "silent",
        "reply_to",
    ):
        if arg in args:
            del args[arg]
    if delete:
        await try_delete(kst)
    if len(text) > MAX_MESSAGE_LEN:
        with suppress(BaseException), BytesIO(str.encode(strip_format(text))) as file:
            file.name = "message.txt"
            await kst.respond(
                r"\\**#Getter**// Message Too Long",
                file=file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to,
                silent=True,
            )
        return await try_delete(kst)
    with suppress(BaseException):
        yy = await kst.client.send_message(
            entity=chat_id,
            message=text,
            link_preview=link_preview,
            silent=silent,
            reply_to=reply_to,
            **args,
        )
    if time:
        await asyncio.sleep(time)
        return await try_delete(yy)
    return yy


async def try_delete(kst):
    with suppress(BaseException):
        return await kst.delete()
