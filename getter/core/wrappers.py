# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from contextlib import suppress
from aiofiles import open as aiopen
from telethon.errors import MessageNotModifiedError
from telethon.tl.types import MessageService
from getter import Root, MAX_MESSAGE_LEN
from getter.core.functions import strip_format


async def eor(
    e,
    text=None,
    link_preview=False,
    silent=False,
    time=None,
    edit_time=None,
    force_reply=False,
    **args,
):
    reply_to = e.reply_to_msg_id or (e if force_reply else None)
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
                reply_to=reply_to,
                silent=True,
            )
        await _try_delete(e)
        return (Root / file).unlink(missing_ok=True)
    if e.out and not isinstance(e, MessageService):
        if edit_time:
            await asyncio.sleep(edit_time)
        try:
            res = await e.edit(
                text,
                link_preview=link_preview,
                **args,
            )
        except MessageNotModifiedError:
            res = e
    else:
        res = await e.client.send_message(
            e.chat_id,
            text,
            link_preview=link_preview,
            silent=silent,
            reply_to=reply_to,
            **args,
        )
    if time:
        await asyncio.sleep(time)
        return await _try_delete(res)
    return res


async def eod(e, text=None, **kwargs):
    kwargs["time"] = kwargs.get("time", 8)
    return await eor(e, text, **kwargs)


async def sod(
    e,
    text=None,
    link_preview=False,
    silent=False,
    time=None,
    edit_time=None,
    force_reply=False,
    delete=True,
    **args,
):
    reply_to = e.reply_to_msg_id or (e if force_reply else None)
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
                reply_to=reply_to,
                silent=True,
            )
        await _try_delete(e)
        return (Root / file).unlink(missing_ok=True)
    res = await e.client.send_message(
        e.chat_id,
        text,
        link_preview=link_preview,
        silent=silent,
        reply_to=reply_to,
        **args,
    )
    if time:
        await asyncio.sleep(time)
        return await _try_delete(res)
    return res


async def _try_delete(e):
    with suppress(BaseException):
        return await e.delete()
