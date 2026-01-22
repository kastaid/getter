# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import re
import sys
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from functools import wraps
from inspect import stack
from io import BytesIO
from pathlib import Path
from traceback import format_exc

from telethon import events, hints
from telethon.errors import (
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
from telethon.tl.types import Message

from getter import (
    __layer__,
    __pyversion__,
    __tlversion__,
    __version__,
)
from getter.config import (
    DEV_CMDS,
    DEVS,
    SUDO_CMDS,
    Var,
    hl,
)

from .base_client import getter_app
from .constants import MAX_MESSAGE_LEN
from .db import gvar
from .functions import admin_check, display_name, to_privilege
from .helper import get_botlogs, jdata
from .property import do_not_remove_credit, get_blacklisted
from .tools import Runner
from .utils import normalize, strip_format, time_formatter

CommandChats = list[int] | set[int] | tuple[int] | None
CommandFunc = Callable[[events.NewMessage.Event], bool | None]


def compile_pattern(
    pattern: str,
    handler: str,
    ignore_case: bool = False,
) -> re.Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    if pattern.startswith(("^", ".")):
        pattern = pattern[1:]
    if handler == " ":
        return re.compile("^" + pattern, flags=flags)
    return re.compile("\\" + handler + pattern, flags=flags)


def kasta_cmd(
    pattern: str | None = None,
    edited: bool = False,
    ignore_case: bool = False,
    no_handler: bool = False,
    no_chats: bool = False,
    users: CommandChats | None = None,
    chats: CommandChats | None = None,
    func: CommandFunc | None = None,
    private_only: bool = False,
    groups_only: bool = False,
    admins_only: bool = False,
    owner_only: bool = False,
    for_dev: bool = False,
    dev: bool = False,
    sudo: bool = False,
    require: str | None = None,
) -> Callable:
    def decorator(fun: Callable) -> None:
        do_not_remove_credit()

        @wraps(fun)
        async def wrapper(kst: Message) -> Callable:
            kst.is_dev = False
            kst.is_sudo = False
            if not kst.out:
                sendby = kst.sender_id
                if dev and sendby in DEVS:
                    kst.is_dev = True
                if sudo and not await gvar("_sudo", use_cache=True):
                    return
                if sendby in await jdata.sudo_users():
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
                    kst.client.log.error(f"({kst.client.full_name} - {myself}) YOU ARE BLACKLISTED !!")
                    sys.exit(1)
            if hasattr(chat, "title") and (
                not (for_dev or dev)
                and "#noub" in chat.title.lower()
                and not (chat.admin_rights or chat.creator)
                and myself not in DEVS
            ):
                return
            if private_only and not kst.is_private:
                return await kst.eod("`Use in private.`")
            if owner_only:
                if kst.is_private:
                    return
                if not chat.creator:
                    return await kst.eod("`Not owner.`")
            if admins_only:
                if kst.is_private:
                    return
                if not (chat.admin_rights or chat.creator):
                    return await kst.eod("`Not an admin.`")
            if require and not (
                await admin_check(
                    kst,
                    chat_id,
                    myself,
                    require=require,
                )
            ):
                return await kst.eod(f"`Required {to_privilege(require)} privilege.`")
            if groups_only and kst.is_private:
                return await kst.eod("`Use in group/channel.`")
            try:
                await fun(kst)
            except FloodWaitError as fw:
                FLOOD_WAIT = fw.seconds
                FLOOD_WAIT_HUMAN = time_formatter((FLOOD_WAIT + 10) * 1000)
                kst.client.log.warning(
                    f"A FloodWait Error of {FLOOD_WAIT}. Sleeping for {FLOOD_WAIT_HUMAN} and try again."
                )
                await asyncio.sleep(FLOOD_WAIT + 10)
                return  # safety first
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
                kst.client.log.critical("STRING_SESSION expired, please create new! Quitting...")
                sys.exit(0)
            except events.StopPropagation:
                raise events.StopPropagation
            except Exception as err:
                kst.client.log.exception(f"[KASTA_CMD] - {err}")
                date = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
                if kst.is_private:
                    chat_type = "private"
                elif kst.is_group:
                    chat_type = "group"
                else:
                    chat_type = "channel"
                ftext = r"\\<b>#Getter_Error</b>// Forward this to @kastaot"
                ftext += "\n\n<b>Getter Version:</b> <code>" + str(__version__)
                ftext += "</code>\n<b>Python Version:</b> <code>" + str(__pyversion__)
                ftext += "</code>\n<b>Telethon Version:</b> <code>" + str(__tlversion__)
                ftext += "</code>\n<b>Telegram Layer:</b> <code>" + str(__layer__) + "</code>\n\n"
                ftext += "<b><u>START GETTER ERROR LOG</u></b>"
                ftext += "\n\n<b>Date:</b> <code>" + date
                ftext += "</code>\n<b>Chat Type:</b> <code>" + chat_type
                ftext += "</code>\n<b>Chat ID:</b> <code>" + str(chat_id)
                ftext += "</code>\n<b>Chat Title:</b> <code>" + normalize(display_name(chat)).upper()
                ftext += "</code>\n<b>User ID:</b> <code>" + str(myself)
                ftext += "</code>\n<b>Is Dev:</b> <code>" + str(kst.is_dev)
                ftext += "</code>\n<b>Is Sudo:</b> <code>" + str(kst.is_sudo)
                ftext += "</code>\n<b>Replied:</b> <code>" + str(kst.is_reply)
                ftext += "</code>\n<b>Message ID:</b> <code>" + str(kst.reply_to_msg_id or kst.id)
                ftext += "</code>\n<b>Message Link:</b> " + str(kst.msg_link)
                ftext += "\n\n<b>Event Trigger:</b>\n<code>"
                ftext += str(kst.text)
                ftext += "</code>\n\n<b>Traceback Info:</b>\n<pre>"
                ftext += str(format_exc()).strip()
                ftext += "</pre>\n\n<b>Error Text:</b>\n<code>"
                ftext += str(sys.exc_info()[1]).strip()
                ftext += "</code>\n\n<b><u>END GETTER ERROR LOG</u></b>"
                if not Var.DEV_MODE:
                    ftext += "\n\n<b>Last 5 Commits:</b>\n<pre>"
                    stdout, stderr, _, _ = await Runner('git log --pretty=format:"%an: %s" -5')
                    result = stdout + stderr
                    ftext += result + "</pre>"
                error_log = None
                BOTLOGS = await get_botlogs()
                send_to = BOTLOGS or chat_id
                reply_to = None if BOTLOGS else kst.id
                if len(ftext) > MAX_MESSAGE_LEN:
                    with suppress(BaseException), BytesIO(str.encode(strip_format(ftext))) as file:
                        file.name = "getter_error.txt"
                        error_log = await getter_app.send_file(
                            send_to,
                            file=file,
                            caption=r"\\<b>#Getter_Error</b>// Forward this to @kastaot",
                            force_document=True,
                            reply_to=reply_to,
                            parse_mode="html",
                        )
                else:
                    error_log = await getter_app.send_message(
                        send_to,
                        ftext,
                        link_preview=False,
                        reply_to=reply_to,
                        parse_mode="html",
                    )
                if kst.out and BOTLOGS and error_log:
                    text = r"\\<b>#Getter_Error</b>//"
                    text += "\n<b>An error details:</b> {}"
                    if kst.is_private:
                        text = text.format(error_log.msg_link)
                    else:
                        text = text.format(f"<code>{error_log.msg_link}</code>")
                    try:
                        await kst.edit(
                            text,
                            link_preview=False,
                            parse_mode="html",
                        )
                    except BaseException:
                        pass

        superuser = dev or sudo
        cmd = None
        if pattern:
            if no_handler:
                handler = " "
            elif dev:
                handler = "$"
            elif sudo:
                handler = ","
            elif Var.NO_HANDLER:
                handler = " "
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
                    from_users=DEVS if for_dev or dev else (jdata.CACHE_DATA.get("sudo") if sudo else users),
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
                from_users=DEVS if for_dev or dev else (jdata.CACHE_DATA.get("sudo") if sudo else users),
                func=lambda e: not e.via_bot_id and func(e) if not (func is None) else not e.via_bot_id,
            ),
        )
        if (pattern and for_dev) or dev or sudo:
            matches = re.split(r"[$(?].*", pattern)
            cmd_name = "".join(matches) if not (for_dev or dev) else pattern
            cmds = DEV_CMDS if for_dev or dev else SUDO_CMDS
            file = Path(stack(0)[1].filename)
            if cmds.get(file.stem):
                cmds[file.stem].append(cmd_name)
            else:
                cmds.update({file.stem: [cmd_name]})
        return wrapper

    return decorator


async def sendlog(
    message: hints.MessageLike,
    forward: bool = False,
    fallback: bool = False,
    **args,
) -> Message | None:
    BOTLOGS = await get_botlogs()
    if not BOTLOGS and fallback:
        BOTLOGS = getter_app.uid
    if not BOTLOGS and not fallback:
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
            fallback=fallback,
            **args,
        )
    except Exception as err:
        getter_app.log.exception(err)
        return None
