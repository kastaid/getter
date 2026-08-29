# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import random
import re

from telethon.errors import (
    FloodPremiumWaitError,
    FloodWaitError,
    SlowModeWaitError,
)

from . import (
    Var,
    get_username,
    hl,
    is_telegram_link,
    kasta_cmd,
    normalize_chat_id,
    plugins_help,
)

PREFIX = "" if Var.NO_HANDLER else hl
DS_RANGE = range(10)
DS_PATTERN = rf"ds({'|'.join(map(str, DS_RANGE[1:]))}|)"
DS_DELAY_MIN = 2
DS_RANDOM_THRESHOLD = 60
DS_RANDOM_DELAY = (3.5, 6.5)
DS_TASKS: dict[int, dict[int, asyncio.Task]] = {i: {} for i in DS_RANGE}
DS_ERROR_MAX = 3
TARGET_RE = re.compile(r"(?:^|\s+)to=(\S+)(?=\s|$)", re.IGNORECASE)


@kasta_cmd(
    pattern=rf"{DS_PATTERN}(?: |$)([\s\S]*)",
)
async def _(kst):
    chat_id, text = await parse_target(kst, kst.text)
    if not chat_id:
        return await kst.eor("Invalid target chat.", time=3)
    ds = int(kst.pattern_match.group(1) or 0)
    ds_name = get_ds_name(ds)
    task_store = get_task_store(ds)
    if chat_id in task_store:
        return await kst.eor(f"Please wait, {ds_name} is running or cancel it.", time=3)
    if kst.is_reply:
        try:
            args = text.split(" ", 2)
            delay = int(args[1])
            count = int(args[2])
            message = await kst.get_reply_message()
            await kst.try_delete()
        except BaseException:
            return await kst.eor(f"`{PREFIX}{ds_name} [delay] [count] [reply] [to=chat]`", time=6)
    else:
        try:
            args = text.split(" ", 3)
            delay = int(args[1])
            count = int(args[2])
            message = str(args[3])
            await kst.try_delete()
        except BaseException:
            return await kst.eor(f"`{PREFIX}{ds_name} [delay] [count] [text] [to=chat]`", time=6)
    delay = max(DS_DELAY_MIN, delay)
    task = asyncio.create_task(
        run_ds(
            kst,
            ds,
            chat_id,
            message,
            delay,
            count,
        )
    )
    DS_TASKS[ds][chat_id] = task
    task.add_done_callback(lambda _, k=chat_id: get_task_store(ds).pop(k, None))


@kasta_cmd(
    pattern=rf"{DS_PATTERN}cancel(?: |$)([\s\S]*)",
)
async def _(kst):
    chat_id, _ = await parse_target(kst, kst.pattern_match.group(2))
    if not chat_id:
        return await kst.eor("Invalid target chat.", time=3)
    ds = int(kst.pattern_match.group(1) or 0)
    ds_name = get_ds_name(ds)
    task_store = get_task_store(ds)
    if chat_id not in task_store:
        return await kst.eor(f"No {ds_name} is running in target chat.", time=3)
    task = task_store.pop(chat_id)
    if not task.done():
        task.cancel()
    await kst.eor(f"`canceled {ds_name} in target chat`", time=6)


@kasta_cmd(
    pattern=rf"{DS_PATTERN}stop$",
)
async def _(kst):
    ds = int(kst.pattern_match.group(1) or 0)
    ds_name = get_ds_name(ds)
    task_store = get_task_store(ds)
    for task in list(task_store.values()):
        if not task.done():
            task.cancel()
    task_store.clear()
    await kst.eor(f"`stopped {ds_name} in all chats`", time=0)


@kasta_cmd(
    pattern="dsclear$",
)
async def _(kst):
    for store in DS_TASKS.values():
        for task in list(store.values()):
            if not task.done():
                task.cancel()
        store.clear()
    await kst.eor("`clear all ds*`", time=0)


def get_ds_name(ds: int) -> str:
    return f"ds{ds}" if ds else "ds"


def get_task_store(ds: int) -> dict[int, asyncio.Task]:
    return DS_TASKS.get(ds)


async def run_ds(
    kst,
    ds: int,
    chat_id: int,
    message: str,
    delay: int,
    count: int,
) -> None:
    error_count = 0
    for _ in range(count):
        if chat_id not in get_task_store(ds):
            break
        try:
            if delay > DS_RANDOM_THRESHOLD:
                await asyncio.sleep(random.uniform(*DS_RANDOM_DELAY))
            await kst.client.send_message(
                chat_id,
                message=message,
                parse_mode="markdown",
                link_preview=True,
                silent=True,
            )
            error_count = 0
            await asyncio.sleep(delay)
        except SlowModeWaitError as err:
            kst.client.log.warning(f"Delayspam {ds} slowmode wait: {err.seconds}s")
            await asyncio.sleep(err.seconds + 5)
        except (
            FloodWaitError,
            FloodPremiumWaitError,
        ) as err:
            wait = err.seconds + random.uniform(15, 30)
            kst.client.log.warning(f"Delayspam {ds} flood wait: {err.seconds}s, sleeping {wait:.1f}s")
            await asyncio.sleep(wait)
        except Exception as err:
            error_count += 1
            if error_count > DS_ERROR_MAX:
                kst.client.log.warning(f"Delayspam {ds} stopped after {error_count} errors in chat {chat_id}: {err}")
                break


async def parse_target(
    kst,
    text: str,
) -> tuple[int | None, str]:
    match = TARGET_RE.search(text)
    target = match.group(1) if match else None
    if match:
        text = text[: match.start()] + text[match.end() :]
    if not target:
        return normalize_chat_id(kst.chat_id), text
    chat_id = normalize_chat_id(target)
    if isinstance(chat_id, int):
        return chat_id, text
    if is_telegram_link(chat_id):
        chat_id = get_username(chat_id)
    try:
        entity = await kst.client.get_entity(chat_id)
        return normalize_chat_id(entity.id), text
    except BaseException:
        return None, text


plugins_help["delayspam"] = {
    f"{PREFIX}ds [delay] [count] [text] [to=chat]": f"Spam a chat in seconds (min {DS_DELAY_MIN} seconds).",
    f"{PREFIX}ds [delay] [count] [reply] [to=chat]": "Spam a replied message to a chat.",
    **{
        f"{PREFIX}ds{x} [delay] [count] [text/reply] [to=chat]": f"Same as above, different message as {x}."
        for x in DS_RANGE[1:]
    },
    f"{PREFIX}dscancel [to=chat]": "To cancel `{PREFIX}ds` in a chat.",
    **{f"{PREFIX}ds{x}cancel [to=chat]": f"To cancel `{PREFIX}ds{x}` in a chat." for x in DS_RANGE[1:]},
    f"{PREFIX}dsstop": "To stop `{PREFIX}ds` in all chats.",
    **{f"{PREFIX}ds{x}stop": f"To stop `{PREFIX}ds{x}` in all chats." for x in DS_RANGE[1:]},
    f"{PREFIX}dsclear": f"""To clear and stop all ds*.

**Notes**:
- `[to=chat]` is optional and can be placed anywhere.
- Without `[to=chat]`, commands use the current chat.
- With `[to=chat]`, commands use the target chat.
- `chat` can be a chat ID, username, or Telegram link.
- Examples: `{PREFIX}ds 5 10 hello`, `{PREFIX}ds 5 10 hello to=username`
- Chat examples: `to=-1001234567890`, `to=username`, `to=https://t.me/username`
""",
}
