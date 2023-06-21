# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from asyncio import sleep
from telethon.errors.rpcerrorlist import FloodWaitError
from . import (
    hl,
    kasta_cmd,
    plugins_help,
    normalize_chat_id,
    DS_TASK,
    DS1_TASK,
    DS2_TASK,
    DS3_TASK,
    DS4_TASK,
)


@kasta_cmd(
    pattern="ds(1|2|3|4|)(?: |$)((?s).*)",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    ds = kst.pattern_match.group(1).strip()
    text = "Please wait until previous •ds{}• finished or cancel it."
    if ds == "1":
        if chat_id in DS1_TASK:
            return await kst.eor(text.format(ds), time=2)
    elif ds == "2":
        if chat_id in DS2_TASK:
            return await kst.eor(text.format(ds), time=2)
    elif ds == "3":
        if chat_id in DS3_TASK:
            return await kst.eor(text.format(ds), time=2)
    elif ds == "4":
        if chat_id in DS4_TASK:
            return await kst.eor(text.format(ds), time=2)
    else:
        if chat_id in DS_TASK:
            return await kst.eor(text.format(ds), time=2)
    if kst.is_reply:
        try:
            args = kst.text.split(" ", 2)
            dly = float(args[1])
            count = int(args[2])
            message = await kst.get_reply_message()
            await kst.try_delete()
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [seconds] [count] [reply]`", time=4)
    else:
        try:
            await kst.try_delete()
            args = kst.text.split(" ", 3)
            dly = float(args[1])
            count = int(args[2])
            message = str(args[3])
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [seconds] [count] [text]`", time=4)
    dly = 2 if dly and int(dly) < 2 else dly
    await ga.mute_chat(chat_id)
    if ds == "1":
        DS1_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS1_TASK:
                break
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except FloodWaitError as fw:
                await sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except BaseException:
                break
        DS1_TASK.discard(chat_id)
    elif ds == "2":
        DS2_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS2_TASK:
                break
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except FloodWaitError as fw:
                await sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except BaseException:
                break
        DS2_TASK.discard(chat_id)
    elif ds == "3":
        DS3_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS3_TASK:
                break
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except FloodWaitError as fw:
                await sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except BaseException:
                break
        DS3_TASK.discard(chat_id)
    elif ds == "4":
        DS4_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS4_TASK:
                break
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except FloodWaitError as fw:
                await sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except BaseException:
                break
        DS4_TASK.discard(chat_id)
    else:
        DS_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS_TASK:
                break
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except FloodWaitError as fw:
                await sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await sleep(dly)
            except BaseException:
                break
        DS_TASK.discard(chat_id)


@kasta_cmd(
    pattern="ds(1|2|3|4|)cancel$",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    ds = kst.pattern_match.group(1).strip()
    text = "No current •ds{}• are running."
    if ds == "1":
        if chat_id not in DS1_TASK:
            return await kst.eor(text.format(ds), time=2)
        DS1_TASK.discard(chat_id)
    elif ds == "2":
        if chat_id not in DS2_TASK:
            return await kst.eor(text.format(ds), time=2)
        DS2_TASK.discard(chat_id)
    elif ds == "3":
        if chat_id not in DS3_TASK:
            return await kst.eor(text.format(ds), time=2)
        DS3_TASK.discard(chat_id)
    elif ds == "4":
        if chat_id not in DS3_TASK:
            return await kst.eor(text.format(ds), time=2)
        DS4_TASK.discard(chat_id)
    else:
        if chat_id not in DS_TASK:
            return await kst.eor(text.format(ds), time=2)
        DS_TASK.discard(chat_id)
    await kst.eor(f"`ds{ds} cancelled`", time=2)


@kasta_cmd(
    pattern="ds(1|2|3|4|)stop$",
)
async def _(kst):
    ds = kst.pattern_match.group(1).strip()
    if ds == "1":
        DS1_TASK.clear()
    elif ds == "2":
        DS2_TASK.clear()
    elif ds == "3":
        DS3_TASK.clear()
    elif ds == "4":
        DS4_TASK.clear()
    else:
        DS_TASK.clear()
    await kst.eor(f"`stopped all ds{ds}`", time=4)


@kasta_cmd(
    pattern="dsclear$",
)
async def _(kst):
    DS_TASK.clear()
    DS1_TASK.clear()
    DS2_TASK.clear()
    DS3_TASK.clear()
    DS4_TASK.clear()
    await kst.eor("`clear all ds*`", time=4)


plugins_help["delayspam"] = {
    "{i}ds [seconds] [count] [reply]/[text]": "Spam current chat in seconds (min 2 seconds).",
    "{i}ds1 [seconds] [count] [reply]/[text]": "Same as above, different message as 1.",
    "{i}ds2 [seconds] [count] [reply]/[text]": "Same as above, different message as 2.",
    "{i}ds3 [seconds] [count] [reply]/[text]": "Same as above, different message as 3.",
    "{i}ds4 [seconds] [count] [reply]/[text]": "Same as above, different message as 4.",
    "{i}dscancel": "To cancel `{i}ds` in current chat.",
    "{i}ds1cancel": "To cancel `{i}ds1` in current chat.",
    "{i}ds2cancel": "To cancel `{i}ds2` in current chat.",
    "{i}ds3cancel": "To cancel `{i}ds3` in current chat.",
    "{i}ds4cancel": "To cancel `{i}ds4` in current chat.",
    "{i}dsstop": "To stop `{i}ds` in all chats.",
    "{i}ds1stop": "To stop `{i}ds1` in all chats.",
    "{i}ds2stop": "To stop `{i}ds2` in all chats.",
    "{i}ds3stop": "To stop `{i}ds3` in all chats.",
    "{i}ds4stop": "To stop `{i}ds4` in all chats.",
    "{i}dsclear": "To stop and clear all ds*.",
}
