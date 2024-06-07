# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from asyncio import sleep
from telethon.errors import RPCError, FloodWaitError, SlowModeWaitError
from . import (
    hl,
    kasta_cmd,
    plugins_help,
    normalize_chat_id,
)

DS_TASKS: dict[int, set[int]] = {i: set() for i in range(10)}


def get_task(ds: str) -> set[int]:
    return DS_TASKS.get(int(ds or 0))


@kasta_cmd(
    pattern=r"ds(1|2|3|4|5|6|7|8|9|)(?: |$)([\s\S]*)",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    ds = kst.pattern_match.group(1).strip()
    task = get_task(ds)
    if chat_id in task:
        return await kst.eor(f"Please wait until previous •ds{ds}• is finished or cancel it.", time=2)
    if kst.is_reply:
        try:
            args = kst.text.split(" ", 2)
            delay = int(args[1])
            count = int(args[2])
            message = await kst.get_reply_message()
            await kst.try_delete()
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [delay] [count] [reply]`", time=4)
    else:
        try:
            args = kst.text_markdown.split(" ", 3)
            delay = int(args[1])
            count = int(args[2])
            message = str(args[3])
            await kst.try_delete()
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [delay] [count] [text]`", time=4)
    delay = 2 if int(delay) < 2 else delay
    task.add(chat_id)
    for _ in range(count):
        if chat_id not in get_task(ds):
            break
        try:
            await ga.send_message(
                chat_id,
                message=message,
                parse_mode="markdown",
                silent=True,
            )
            await sleep(delay)
        except FloodWaitError as fw:
            await sleep(fw.seconds)
            await ga.send_message(
                chat_id,
                message=message,
                parse_mode="markdown",
                silent=True,
            )
            await sleep(delay)
        except SlowModeWaitError:
            pass
        except RPCError:
            break
    get_task(ds).discard(chat_id)


@kasta_cmd(
    pattern="ds(1|2|3|4|5|6|7|8|9|)cancel$",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    ds = kst.pattern_match.group(1).strip()
    task = get_task(ds)
    if chat_id not in task:
        return await kst.eor(f"No running •ds{ds}• in current chat.", time=2)
    task.discard(chat_id)
    await kst.eor(f"`cancelled ds{ds} in current chat`", time=2)


@kasta_cmd(
    pattern="ds(1|2|3|4|5|6|7|8|9|)stop$",
)
async def _(kst):
    ds = kst.pattern_match.group(1).strip()
    get_task(ds).clear()
    await kst.eor(f"`stopped ds{ds} in all chats`", time=4)


@kasta_cmd(
    pattern="dsclear$",
)
async def _(kst):
    for task in DS_TASKS.values():
        task.clear()
    await kst.eor("`clear all ds*`", time=4)


plugins_help["delayspam"] = {
    "{i}ds [delay] [count] [text]/[reply]": "Spam current chat in seconds (min 2 seconds).",
    "{i}ds1 [delay] [count] [text]/[reply]": "Same as above, different message as 1.",
    "{i}ds2 [delay] [count] [text]/[reply]": "Same as above, different message as 2.",
    "{i}ds3 [delay] [count] [text]/[reply]": "Same as above, different message as 3.",
    "{i}ds4 [delay] [count] [text]/[reply]": "Same as above, different message as 4.",
    "{i}ds5 [delay] [count] [text]/[reply]": "Same as above, different message as 5.",
    "{i}ds6 [delay] [count] [text]/[reply]": "Same as above, different message as 6.",
    "{i}ds7 [delay] [count] [text]/[reply]": "Same as above, different message as 7.",
    "{i}ds8 [delay] [count] [text]/[reply]": "Same as above, different message as 8.",
    "{i}ds9 [delay] [count] [text]/[reply]": "Same as above, different message as 9.",
    "{i}dscancel": "To cancel `{i}ds` in current chat.",
    "{i}ds1cancel": "To cancel `{i}ds1` in current chat.",
    "{i}ds2cancel": "To cancel `{i}ds2` in current chat.",
    "{i}ds3cancel": "To cancel `{i}ds3` in current chat.",
    "{i}ds4cancel": "To cancel `{i}ds4` in current chat.",
    "{i}ds5cancel": "To cancel `{i}ds5` in current chat.",
    "{i}ds6cancel": "To cancel `{i}ds6` in current chat.",
    "{i}ds7cancel": "To cancel `{i}ds7` in current chat.",
    "{i}ds8cancel": "To cancel `{i}ds8` in current chat.",
    "{i}ds9cancel": "To cancel `{i}ds9` in current chat.",
    "{i}dsstop": "To stop `{i}ds` in all chats.",
    "{i}ds1stop": "To stop `{i}ds1` in all chats.",
    "{i}ds2stop": "To stop `{i}ds2` in all chats.",
    "{i}ds3stop": "To stop `{i}ds3` in all chats.",
    "{i}ds4stop": "To stop `{i}ds4` in all chats.",
    "{i}ds5stop": "To stop `{i}ds5` in all chats.",
    "{i}ds6stop": "To stop `{i}ds6` in all chats.",
    "{i}ds7stop": "To stop `{i}ds7` in all chats.",
    "{i}ds8stop": "To stop `{i}ds8` in all chats.",
    "{i}ds9stop": "To stop `{i}ds9` in all chats.",
    "{i}dsclear": "To clear and stop all ds*.",
}
