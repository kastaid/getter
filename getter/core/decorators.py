# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import datetime
import re
import sys
from contextlib import suppress
from io import BytesIO
from traceback import format_exc
from typing import (
    Union,
    Callable,
    Set,
    List,
    Tuple,
    Optional,
)
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
from telethon.events import MessageEdited, NewMessage, StopPropagation
from telethon.tl.custom.message import Message
from .. import (
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
    DEVS,
    MAX_MESSAGE_LEN,
)
from ..config import Var, HANDLER
from ..logger import LOGS
from .client import getter_app
from .functions import (
    display_name,
    strip_format,
    time_formatter,
    Runner,
)
from .property import do_not_remove_credit, get_blacklisted
from .wrappers import (
    eor,
    eod,
    sod,
    _try_delete,
)

CommandFunc = Callable[[NewMessage.Event], Union[bool, None]]
CommandChats = Union[List[int], Set[int], Tuple[int], None]


def compile_pattern(
    pattern: str,
    handler: str,
    ignore_case: bool = False,
):
    flags = re.I if ignore_case else 0
    if pattern.startswith(("^", ".")):
        pattern = pattern[1:]
    if handler == " ":
        return re.compile("^" + pattern, flags=flags)
    return re.compile("\\" + handler + pattern, flags=flags)


def kasta_cmd(
    pattern: Union[str, None] = None,
    no_handler: bool = False,
    ignore_case: bool = False,
    edited: bool = False,
    chats: Optional[CommandChats] = None,
    blacklist_chats: bool = False,
    func: Optional[CommandFunc] = None,
    senders: Optional[CommandChats] = None,
    own: bool = False,
    no_crash: bool = False,
    private_only: bool = False,
    groups_only: bool = False,
    admins_only: bool = False,
) -> Callable:
    is_own = True if own and senders else False

    def decor(fun):
        do_not_remove_credit()

        async def wrapp(kst):
            chat = kst.chat
            user_id = kst.client.uid
            if user_id not in DEVS:
                KASTA_BLACKLIST = await get_blacklisted(
                    url="https://raw.githubusercontent.com/kastaid/resources/main/kastablacklist.py",
                    attempts=3,
                    fallbacks=[],
                )
                if user_id in KASTA_BLACKLIST:
                    LOGS.error(
                        "({} - {}) YOU ARE BLACKLISTED !!".format(
                            kst.client.full_name,
                            user_id,
                        )
                    )
                    sys.exit(1)
            if hasattr(chat, "title"):
                if (
                    not is_own
                    and "#noub" in chat.title.lower()
                    and not (chat.admin_rights or chat.creator)
                    and not (user_id in DEVS)
                ):
                    return
            if private_only and not kst.is_private:
                return await eod(kst, "`use in private`")
            if admins_only:
                if kst.is_private:
                    return
                if not (chat.admin_rights or chat.creator):
                    return await eod(kst, "`not admin`")
            if groups_only and kst.is_private:
                return await eod(kst, "`use in group or channel`")
            try:
                await fun(kst)
            except FloodWaitError as fw:
                FLOOD_WAIT = fw.seconds
                FLOOD_WAIT_HUMAN = time_formatter((FLOOD_WAIT + 10) * 1000)
                LOGS.warning(f"A FloodWait Error of {FLOOD_WAIT}. Sleeping for {FLOOD_WAIT_HUMAN} and try again.")
                await _try_delete(kst)
                await asyncio.sleep(FLOOD_WAIT + 10)
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
                KeyboardInterrupt,
            ):
                pass
            except AuthKeyDuplicatedError:
                LOGS.critical("STRING_SESSION expired, please create new! Quitting...")
                sys.exit(0)
            except StopPropagation:
                raise StopPropagation
            except Exception as err:
                LOGS.exception(f"[KASTA_CMD] - {err}")
                if not no_crash:
                    date = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
                    ftext = r"\\**#Getter**// **Client Error:** Forward this to @kastaot"
                    ftext += "\n\n**Getter Version:** `" + str(__version__)
                    ftext += "`\n**Python Version:** `" + str(__pyversion__)
                    ftext += "`\n**Telethon Version:** `" + str(__tlversion__)
                    ftext += "`\n**Telegram Layer:** `" + str(__layer__) + "`\n\n"
                    ftext += "--------START GETTER CRASH LOG--------"
                    ftext += "\n\n**Date:** `" + date
                    ftext += "`\n**Chat:** `" + str(kst.chat_id) + " " + display_name(chat) + "`"
                    ftext += "\n**User ID:** `" + str(user_id)
                    ftext += "`\n**Replied:** `" + str(kst.is_reply)
                    ftext += "`\n\n**Event Trigger:**`\n"
                    ftext += str(kst.text)
                    ftext += "`\n\n**Traceback Info:**`\n"
                    ftext += str(format_exc())
                    ftext += "`\n\n**Error Text:**`\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "`\n\n--------END GETTER CRASH LOG--------"
                    if not Var.DEV_MODE:
                        ftext += "\n\n\n**Last 5 Commits:**`\n"
                        stdout, stderr, _, _ = await Runner('git log --pretty=format:"%an: %s" -5')
                        result = stdout + (stderr or "")
                        ftext += result + "`"

                    if len(ftext) > MAX_MESSAGE_LEN:
                        with suppress(BaseException):
                            ftext = strip_format(ftext)
                            with BytesIO(ftext.encode()) as file:
                                file.name = "getter_client_error.txt"
                                await getter_app.send_file(
                                    kst.chat_id,
                                    file=file,
                                    caption=r"\\**#Getter**// **Client Error:** Forward this to @kastaot",
                                    force_document=True,
                                    allow_cache=False,
                                    reply_to=kst.id,
                                    silent=True,
                                )
                    else:
                        await getter_app.send_message(
                            kst.chat_id,
                            ftext,
                            link_preview=False,
                            reply_to=kst.id,
                            silent=True,
                        )

        cmd = None
        if pattern:
            handler = " " if no_handler else ("$" if is_own else HANDLER)
            cmd = compile_pattern(
                pattern=pattern,
                handler=handler,
                ignore_case=ignore_case,
            )
        if edited:

            def funce_(e):
                if not (func is None):
                    return not e.via_bot_id and func(e) and not (e.is_channel and e.chat.broadcast)
                return not e.via_bot_id and not (e.is_channel and e.chat.broadcast)

            getter_app.add_event_handler(
                callback=wrapp,
                event=MessageEdited(
                    chats=chats,
                    blacklist_chats=blacklist_chats,
                    func=funce_,
                    incoming=True if is_own else None,
                    outgoing=True if not is_own else None,
                    from_users=senders,
                    forwards=None if is_own else False,
                    pattern=cmd,
                ),
            )

        def funcn_(e):
            if not (func is None):
                return not e.via_bot_id and func(e)
            return not e.via_bot_id

        getter_app.add_event_handler(
            callback=wrapp,
            event=NewMessage(
                chats=chats,
                blacklist_chats=blacklist_chats,
                func=funcn_,
                incoming=True if is_own else None,
                outgoing=True if not is_own else None,
                from_users=senders,
                forwards=None if is_own else False,
                pattern=cmd,
            ),
        )
        return wrapp

    return decor


Message.eor = eor
Message.eod = eod
Message.sod = sod
Message.try_delete = _try_delete
