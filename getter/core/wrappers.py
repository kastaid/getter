# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import typing
from contextlib import suppress
from io import BytesIO
from telethon import hints
from telethon.errors.rpcerrorlist import MessageIdInvalidError, MessageNotModifiedError
from telethon.tl import types as typ
from ..config import MAX_MESSAGE_LEN
from .utils import strip_format


async def eor(
    message: typ.Message,
    text: str,
    link_preview: bool = False,
    silent: bool = False,
    time: typing.Optional[typing.Union[int, float]] = None,
    edit_time: typing.Optional[typing.Union[int, float]] = None,
    force_reply: bool = False,
    **args,
) -> typing.Optional[typing.Union[typ.Message, typing.Sequence[typ.messages.AffectedMessages]]]:
    _ = args.get("reply_to", None)
    reply_to = _ if _ else (message.reply_to_msg_id or (message if force_reply else None))
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
            await message.respond(
                r"\\**#Getter**// Message Too Long",
                file=file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to,
                silent=True,
            )
        if message.out:
            return await _try_delete(message)
    if message.out and not isinstance(message, typ.MessageService):
        if edit_time:
            await asyncio.sleep(edit_time)
        try:
            yy = await message.edit(
                text,
                link_preview=link_preview,
                **args,
            )
        except MessageIdInvalidError:  # keep functions running
            return None
        except MessageNotModifiedError:
            yy = message
    else:
        with suppress(BaseException):
            yy = await message.respond(
                message=text,
                link_preview=link_preview,
                silent=silent,
                reply_to=reply_to,
                **args,
            )
    if yy and time:
        await asyncio.sleep(time)
        return await _try_delete(yy)
    return yy


async def eod(
    message: typ.Message,
    text: str,
    **kwargs,
) -> typing.Optional[typing.Union[typ.Message, typing.Sequence[typ.messages.AffectedMessages]]]:
    kwargs["time"] = kwargs.get("time", 8)
    return await eor(message, text, **kwargs)


async def sod(
    message: typ.Message,
    text: str,
    chat_id: typing.Optional[hints.EntityLike] = None,
    link_preview: bool = False,
    silent: bool = False,
    time: typing.Optional[typing.Union[int, float]] = None,
    edit_time: typing.Optional[typing.Union[int, float]] = None,
    force_reply: bool = False,
    delete: bool = True,
    **args,
) -> typing.Optional[typing.Union[typ.Message, typing.Sequence[typ.messages.AffectedMessages]]]:
    chat_id = chat_id or message.chat_id
    _ = args.get("reply_to", None)
    reply_to = _ if _ else (message.reply_to_msg_id or (message if force_reply else None))
    for arg in (
        "entity",
        "message",
        "link_preview",
        "silent",
        "reply_to",
    ):
        if arg in args:
            del args[arg]
    if len(text) > MAX_MESSAGE_LEN:
        with suppress(BaseException), BytesIO(str.encode(strip_format(text))) as file:
            file.name = "message.txt"
            await message.respond(
                r"\\**#Getter**// Message Too Long",
                file=file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to,
                silent=True,
            )
        if message.out:
            return await _try_delete(message)
    if message.out and delete:
        await _try_delete(message)
    with suppress(BaseException):
        yy = await message.client.send_message(
            entity=chat_id,
            message=text,
            link_preview=link_preview,
            silent=silent,
            reply_to=reply_to,
            **args,
        )
    if yy and time:
        await asyncio.sleep(time)
        return await _try_delete(yy)
    return yy


async def _try_delete(message: typ.Message) -> typing.Optional[typing.Sequence[typ.messages.AffectedMessages]]:
    with suppress(BaseException):
        return await message.delete()
    return None


async def _react(message: typ.Message, *args, **kwargs) -> typing.Optional[typ.Updates]:
    kwargs["message"] = message.id
    return await message.client.send_reaction(await message.get_input_chat(), *args, **kwargs)
