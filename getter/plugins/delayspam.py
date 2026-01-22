# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio

from telethon.errors import FloodWaitError, RPCError, SlowModeWaitError

from . import (
    hl,
    kasta_cmd,
    normalize_chat_id,
    plugins_help,
)

DS_TASKS: dict[int, dict[int, asyncio.Task]] = {i: {} for i in range(10)}


def get_task_store(ds: int) -> dict[int, asyncio.Task]:
    return DS_TASKS.get(ds)


@kasta_cmd(
    pattern=r"ds(1|2|3|4|5|6|7|8|9|)(?: |$)([\s\S]*)",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    ds = int(kst.pattern_match.group(1) or 0)
    task_store = get_task_store(ds)
    if chat_id in task_store:
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
            args = kst.text.split(" ", 3)
            delay = int(args[1])
            count = int(args[2])
            message = str(args[3])
            await kst.try_delete()
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [delay] [count] [text]`", time=4)
    delay = max(2, delay)
    task = asyncio.create_task(
        run_delayspam(
            kst,
            ds,
            chat_id,
            message,
            delay,
            count,
        )
    )
    DS_TASKS[ds][chat_id] = task
    task.add_done_callback(lambda t, k=chat_id: get_task_store(ds).pop(k, None))


@kasta_cmd(
    pattern="ds(1|2|3|4|5|6|7|8|9|)cancel$",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    ds = int(kst.pattern_match.group(1) or 0)
    task_store = get_task_store(ds)
    if chat_id not in task_store:
        return await kst.eor(f"No running •ds{ds}• in current chat.", time=2)
    task = task_store.pop(chat_id)
    if not task.done():
        task.cancel()
    await kst.eor(f"`canceled ds{ds} in current chat`", time=2)


@kasta_cmd(
    pattern="ds(1|2|3|4|5|6|7|8|9|)stop$",
)
async def _(kst):
    ds = int(kst.pattern_match.group(1) or 0)
    task_store = get_task_store(ds)
    for task in list(task_store.values()):
        if not task.done():
            task.cancel()
    task_store.clear()
    await kst.eor(f"`stopped ds{ds} in all chats`", time=4)


@kasta_cmd(
    pattern="dsclear$",
)
async def _(kst):
    for store in DS_TASKS.values():
        for task in list(store.values()):
            if not task.done():
                task.cancel()
        store.clear()
    await kst.eor("`clear all ds*`", time=4)


async def run_delayspam(
    kst,
    ds: int,
    chat_id: int,
    message: str,
    delay: int,
    count: int,
) -> None:
    for _ in range(count):
        if chat_id not in get_task_store(ds):
            break
        try:
            await kst.client.send_message(
                chat_id,
                message=message,
                parse_mode="markdown",
                silent=True,
            )
            await asyncio.sleep(delay)
        except FloodWaitError as fw:
            await asyncio.sleep(fw.seconds)
            await kst.client.send_message(
                chat_id,
                message=message,
                parse_mode="markdown",
                silent=True,
            )
            await asyncio.sleep(delay)
        except SlowModeWaitError:
            pass
        except RPCError:
            break


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
