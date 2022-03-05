# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import re
import sys
from asyncio import CancelledError, sleep
from contextlib import suppress
from datetime import datetime, timezone
from io import BytesIO
from platform import python_version
from traceback import format_exc
from telethon import events, version
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
from getter import __version__
from getter.app import App
from getter.config import HANDLER
from getter.logger import LOGS
from getter.utils import (
    display_name,
    md_to_text,
    time_formatter,
    Runner,
)


def compile_pattern(data, handler):
    if data.startswith(("^", ".")):
        data = data[1:]
    if handler == "\\ ":
        return re.compile("^" + data)
    return re.compile(handler + data)


def kasta_cmd(pattern=None, **kwargs):
    disable_errors = kwargs.get("disable_errors", False)
    func = kwargs.get("func", lambda e: not e.via_bot_id)
    senders = kwargs.get("senders", None)
    chats = kwargs.get("chats", None)
    blacklist_chats = kwargs.get("blacklist_chats", False)
    own = kwargs.get("own", False)

    def decorator(kasta):
        async def wrapper(check):
            chat = check.chat
            chat_id = check.chat_id or check.from_id
            try:
                await kasta(check)
            except FloodWaitError as e:
                FLOOD_WAIT = e.seconds
                FLOOD_WAIT_HUMAN = time_formatter((FLOOD_WAIT + 5) * 1000)
                LOGS.error(f"A FloodWait Error of {FLOOD_WAIT}. Sleeping for {FLOOD_WAIT_HUMAN} and try again.")
                with suppress(BaseException):
                    await check.delete()
                await sleep(FLOOD_WAIT + 5)
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
                CancelledError,
                ConnectionError,
                KeyboardInterrupt,
                SystemExit,
            ):
                pass
            except AuthKeyDuplicatedError:
                LOGS.error("STRING_SESSION expired, please create new! Quitting...")
                sys.exit(0)
            except events.StopPropagation:
                raise events.StopPropagation
            except Exception as e:
                LOGS.exception(f"[COMMAND] - {e}")
                if not disable_errors:
                    date = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
                    title = display_name(chat)
                    ftext = "**Getter Client Error:** `Forward this to` @kastaot\n\n"
                    ftext += "**Getter Version:** `" + str(__version__)
                    ftext += "`\n**Python Version:** `" + str(python_version())
                    ftext += "`\n**Telethon Version:** `" + str(version.__version__) + "`\n\n"
                    ftext += "--------START GETTER CRASH LOG--------"
                    ftext += "\n\n**Date:** `" + date
                    ftext += "`\n**Chat:** `" + str(chat_id) + "` " + str(title)
                    ftext += "\n**User ID:** `" + str(check.sender_id)
                    ftext += "`\n**Replied:** `" + str(check.is_reply)
                    ftext += "`\n\n**Event Trigger:**`\n"
                    ftext += str(check.text)
                    ftext += "`\n\n**Traceback Info:**`\n"
                    ftext += str(format_exc())
                    ftext += "`\n\n**Error Text:**`\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "`\n\n--------END GETTER CRASH LOG--------"
                    ftext += "\n\n\n**Last 5 Commits:**`\n"
                    stdout, stderr = await Runner('git log --pretty=format:"%an: %s" -5')
                    result = stdout + stderr
                    ftext += result + "`"

                    with suppress(BaseException):
                        if len(ftext) > 4096:
                            ftext = md_to_text(ftext)
                            with BytesIO(ftext.encode()) as file:
                                file.name = "getter_client_error.txt"
                                await App.send_file(
                                    chat_id,
                                    file=file,
                                    caption="**Getter Client Error:** `Forward this to` @kastaot\n\n",
                                    force_document=True,
                                    allow_cache=False,
                                )
                        else:
                            await App.send_message(
                                chat_id,
                                ftext,
                                link_preview=False,
                                silent=True,
                            )

        cmd = None
        is_own = True if own and senders else False
        if pattern:
            hl = "$" if is_own else HANDLER
            cmd = compile_pattern(pattern, "\\" + hl)
        App.add_event_handler(
            wrapper,
            events.NewMessage(
                chats=chats,
                blacklist_chats=blacklist_chats,
                func=func,
                incoming=True if is_own else None,
                outgoing=True if not is_own else None,
                from_users=senders,
                forwards=None if is_own else False,
                pattern=cmd,
            ),
        )
        return wrapper

    return decorator
