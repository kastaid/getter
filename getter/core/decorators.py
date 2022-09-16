# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import datetime
import inspect
import re
import sys
import typing
from contextlib import suppress
from functools import wraps
from io import BytesIO
from pathlib import Path
from traceback import format_exc
from telethon import events
from telethon.errors.rpcerrorlist import (
    AuthKeyDuplicatedError,
    ChatSendGifsForbiddenError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    ChatWriteForbiddenError,
    FloodWaitError,
    MessageDeleteForbiddenError,
    MessageIdInvalidError,
    MessageNotModifiedError,
)
from telethon.tl import types as typ
from telethon.tl.custom.message import Message
from .. import (
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
)
from ..config import (
    Var,
    hl,
    DEV_CMDS,
    SUDO_CMDS,
    DEVS,
    MAX_MESSAGE_LEN,
)
from ..logger import LOGS
from .client import getter_app
from .db import gvar
from .functions import display_name, admin_check, to_privilege
from .helper import jdata, get_botlogs
from .property import do_not_remove_credit, get_blacklisted
from .tools import Runner
from .utils import strip_format, time_formatter
from .wrappers import (
    eor,
    eod,
    sod,
    try_delete,
)

CommandChats = typing.Union[typing.List[int], typing.Set[int], typing.Tuple[int], None]
CommandFunc = typing.Callable[[events.NewMessage.Event], typing.Optional[bool]]


def compile_pattern(
    pattern: str,
    handler: str,
    ignore_case: bool = False,
) -> re.Pattern:
    flags = re.I if ignore_case else 0
    if pattern.startswith(("^", ".")):
        pattern = pattern[1:]
    if handler == " ":
        return re.compile("^" + pattern, flags=flags)
    return re.compile("\\" + handler + pattern, flags=flags)


def kasta_cmd(
    pattern: typing.Optional[str] = None,
    edited: bool = False,
    ignore_case: bool = False,
    no_handler: bool = False,
    no_crash: bool = False,
    no_chats: bool = False,
    users: typing.Optional[CommandChats] = None,
    chats: typing.Optional[CommandChats] = None,
    func: typing.Optional[CommandFunc] = None,
    private_only: bool = False,
    groups_only: bool = False,
    admins_only: bool = False,
    owner_only: bool = False,
    for_dev: bool = False,
    dev: bool = False,
    sudo: bool = False,
    require: typing.Optional[str] = None,
) -> typing.Callable:
    def decorator(fun) -> None:
        do_not_remove_credit()

        @wraps(fun)
        async def wrapper(kst) -> typing.Callable:
            kst.is_dev = False
            kst.is_sudo = False
            if not kst.out:
                sendby = kst.sender_id
                if dev and sendby in DEVS:
                    kst.is_dev = True
                if sudo and not gvar("_sudo", use_cache=True):
                    return
                if sendby in jdata.sudo_users:
                    kst.is_sudo = True
            chat = kst.chat
            chat_id = kst.chat_id
            myself = kst.client.uid
            if myself not in DEVS:
                KASTA_BLACKLIST = await get_blacklisted(
                    url="https://raw.githubusercontent.com/kastaid/resources/main/kastablacklist.py",
                    attempts=3,
                    fallbacks=None,
                )
                if myself in KASTA_BLACKLIST:
                    LOGS.error(
                        "({} - {}) YOU ARE BLACKLISTED !!".format(
                            kst.client.full_name,
                            myself,
                        )
                    )
                    sys.exit(1)
            if hasattr(chat, "title") and (
                not (for_dev or dev)
                and "#noub" in chat.title.lower()
                and not (chat.admin_rights or chat.creator)
                and myself not in DEVS
            ):
                return
            if private_only and not kst.is_private:
                return await eod(kst, "`Use in private.`")
            if owner_only:
                if kst.is_private:
                    return
                if not chat.creator:
                    return await eod(kst, "`Not owner.`")
            if admins_only:
                if kst.is_private:
                    return
                if not (chat.admin_rights or chat.creator):
                    return await eod(kst, "`Not an admin.`")
            if require and not (
                await admin_check(
                    kst,
                    chat_id,
                    myself,
                    require=require,
                )
            ):
                return await eod(kst, f"`Required {to_privilege(require)} privilege.`")
            if groups_only and kst.is_private:
                return await eod(kst, "`Use in group/channel.`")
            try:
                await fun(kst)
            except FloodWaitError as fw:
                FLOOD_WAIT = fw.seconds
                FLOOD_WAIT_HUMAN = time_formatter((FLOOD_WAIT + 10) * 1000)
                LOGS.warning(f"A FloodWait Error of {FLOOD_WAIT}. Sleeping for {FLOOD_WAIT_HUMAN} and try again.")
                await try_delete(kst)
                await getter_app.disconnect()
                await asyncio.sleep(FLOOD_WAIT + 10)
                await getter_app.connect()
                return
            except (
                MessageIdInvalidError,
                MessageNotModifiedError,
                MessageDeleteForbiddenError,
                ChatWriteForbiddenError,
                ChatSendMediaForbiddenError,
                ChatSendGifsForbiddenError,
                ChatSendStickersForbiddenError,
                ChatSendInlineForbiddenError,
                ConnectionError,
                KeyboardInterrupt,
            ):
                pass
            except AuthKeyDuplicatedError:
                LOGS.critical("STRING_SESSION expired, please create new! Quitting...")
                sys.exit(0)
            except events.StopPropagation:
                raise events.StopPropagation
            except Exception as err:
                LOGS.exception(f"[KASTA_CMD] - {err}")
                if not no_crash:
                    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    if kst.is_private:
                        chat_type = "private"
                    elif kst.is_group:
                        chat_type = "group"
                    else:
                        chat_type = "channel"
                    ftext = r"\\**#Getter_Error**// Forward this to @kastaot"
                    ftext += "\n\n**Getter Version:** `" + str(__version__)
                    ftext += "`\n**Python Version:** `" + str(__pyversion__)
                    ftext += "`\n**Telethon Version:** `" + str(__tlversion__)
                    ftext += "`\n**Telegram Layer:** `" + str(__layer__) + "`\n\n"
                    ftext += "**--START GETTER ERROR LOG--**"
                    ftext += "\n\n**Date:** `" + date
                    ftext += "`\n**Chat Type:** `" + chat_type
                    ftext += "`\n**Chat ID:** `" + str(chat_id)
                    ftext += "`\n**Chat Title:** `" + display_name(chat)
                    ftext += "`\n**User ID:** `" + str(myself)
                    ftext += "`\n**Replied:** `" + str(kst.is_reply)
                    ftext += "`\n\n**Event Trigger:**`\n"
                    ftext += str(kst.text)
                    ftext += "`\n\n**Traceback Info:**```\n"
                    ftext += str(format_exc())
                    ftext += "```\n\n**Error Text:**`\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "`\n\n**--END GETTER ERROR LOG--**"
                    if not Var.DEV_MODE:
                        ftext += "\n\n\n**Last 5 Commits:**`\n"
                        stdout, stderr, _, _ = await Runner('git log --pretty=format:"%an: %s" -5')
                        result = stdout + stderr
                        ftext += result + "`"
                    error_log = None
                    BOTLOGS = get_botlogs()
                    send_to = BOTLOGS or chat_id
                    reply_to = None if BOTLOGS else kst.id
                    if len(ftext) > MAX_MESSAGE_LEN:
                        with suppress(BaseException), BytesIO(str.encode(strip_format(ftext))) as file:
                            file.name = "getter_error.txt"
                            error_log = await getter_app.send_file(
                                send_to,
                                file=file,
                                caption=r"\\**#Getter_Error**// Forward this to @kastaot",
                                force_document=True,
                                allow_cache=False,
                                reply_to=reply_to,
                            )
                    else:
                        error_log = await getter_app.send_message(
                            send_to,
                            ftext,
                            link_preview=False,
                            reply_to=reply_to,
                        )
                    if kst.out and BOTLOGS and error_log:
                        text = r"\\<b>#Getter_Error</b>// An error occurred, check the error here: {}".format(
                            error_log.message_link if kst.is_private else f"<code>{error_log.message_link}</code>",
                        )
                        with suppress(BaseException):
                            await kst.edit(
                                text,
                                link_preview=False,
                                parse_mode="html",
                            )

        superuser = dev or sudo
        cmd = None
        if pattern:
            if no_handler:
                handler = " "
            elif dev:
                handler = "$"
            elif sudo:
                handler = ","
            else:
                handler = hl
            cmd = compile_pattern(
                pattern=pattern,
                handler=handler,
                ignore_case=ignore_case,
            )
        if edited:
            getter_app.add_event_handler(
                wrapper,
                event=events.MessageEdited(
                    pattern=cmd,
                    chats=None if for_dev or dev else chats,
                    blacklist_chats=False if for_dev or dev else no_chats,
                    incoming=True if superuser else None,
                    outgoing=True if not superuser else None,
                    forwards=None if for_dev or dev else False,
                    from_users=DEVS if for_dev or dev else (jdata.sudo_users if sudo else users),
                    func=lambda e: not e.via_bot_id and func(e) and not (e.is_channel and e.chat.broadcast)
                    if not (func is None)
                    else not e.via_bot_id and not (e.is_channel and e.chat.broadcast),
                ),
            )
        getter_app.add_event_handler(
            wrapper,
            event=events.NewMessage(
                pattern=cmd,
                chats=None if for_dev or dev else chats,
                blacklist_chats=False if for_dev or dev else no_chats,
                incoming=True if superuser else None,
                outgoing=True if not superuser else None,
                forwards=None if for_dev or dev else False,
                from_users=DEVS if for_dev or dev else (jdata.sudo_users if sudo else users),
                func=lambda e: not e.via_bot_id and func(e) if not (func is None) else not e.via_bot_id,
            ),
        )
        if pattern and for_dev or dev or sudo:
            file = Path(inspect.stack(0)[1].filename)
            cmd_name = "".join(re.split(r"[$(?].*", pattern)) if not (for_dev or dev) else pattern
            cmds = DEV_CMDS if for_dev or dev else SUDO_CMDS
            if cmds.get(file.stem):
                cmds[file.stem].append(cmd_name)
            else:
                cmds.update({file.stem: [cmd_name]})
        return wrapper

    return decorator


async def sendlog(
    message: typ.Message,
    forward: bool = False,
    **args,
) -> typing.Optional[typ.Message]:
    BOTLOGS = get_botlogs()
    if not BOTLOGS:
        return None
    try:
        if not forward:
            return await getter_app.send_message(
                entity=BOTLOGS,
                message=message,
                **args,
            )
        return await getter_app.forward_messages(
            entity=BOTLOGS,
            messages=message,
            **args,
        )
    except FloodWaitError as fw:
        await asyncio.sleep(fw.seconds + 10)
        return await sendlog(
            message=message,
            forward=forward,
            **args,
        )
    except Exception as err:
        LOGS.exception(err)
        return None


Message.eor = eor
Message.eod = eod
Message.sod = sod
Message.try_delete = try_delete
