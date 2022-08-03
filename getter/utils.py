# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
from functools import partial
from re import IGNORECASE, match, sub
from typing import Union
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from emoji import replace_emoji
from markdown import markdown
from telethon.tl.types import MessageEntityMentionName, MessageEntityPre
from telethon.utils import add_surrogate, get_display_name

tlink_re = r"^(?:https?://)((www)\.|)(?:t\.me|telegram\.(?:dog|me))/(\w+)$"
tusername_re = r"^(?:https?://)((www)\.|)(?:t\.me|telegram\.(?:dog|me))/"


def is_telegram_link(url: str) -> bool:
    return bool(match(tlink_re, url, flags=IGNORECASE))


def get_username(url: str) -> str:
    return sub(tusername_re, "@", url, flags=IGNORECASE)


def display_name(user) -> str:
    name = get_display_name(user)
    return name if name else "{}".format(user.first_name)


def md_to_text(md: str) -> str:
    html = markdown(md)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()


def parse_pre(text: str) -> str:
    text = text.strip()
    return (
        text,
        [MessageEntityPre(offset=0, length=len(add_surrogate(text)), language="")],
    )


def deEmojify(inputString: str) -> str:
    return replace_emoji(inputString, "")


def humanbytes(size: Union[int, float]) -> str:
    if not size:
        return "0B"
    for _ in ["", "K", "M", "G", "T"]:
        if size < 1024:
            break
        size /= 1024
    if isinstance(size, int):
        size = f"{size}{_}B"
    elif isinstance(size, float):
        size = f"{size:.2f}{_}B"
    return size


def time_formatter(ms: Union[int, str]) -> str:
    minutes, seconds = divmod(int(ms / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s") if seconds else "")
    )
    if tmp:
        return tmp[:-1] if tmp.endswith(":") else tmp
    else:
        return "0s"


async def Runner(cmd: str) -> (bytes, bytes):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


async def Searcher(
    url: str,
    post: bool = None,
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    data: dict = None,
    ssl=None,
    re_json: bool = False,
    re_content: bool = False,
    real: bool = False,
):
    async with ClientSession(headers=headers) as client:
        try:
            if post:
                data = await client.post(url, json=json, data=data, ssl=ssl)
            else:
                data = await client.get(url, params=params, ssl=ssl)
        except asyncio.exceptions.TimeoutError:
            return None
        if data.status == 404 or data.status not in (200, 201):
            return None
        if re_json:
            return await data.json(content_type=None)
        if re_content:
            return await data.read()
        if real:
            return data
        return await data.text()


async def get_user(event, group=1):
    from getter.logger import LOGS

    args = event.pattern_match.group(group).split(" ", 1)
    extra = None
    await event.get_chat()
    try:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
                user = int(user)
            if event.message.entities:
                probable_mention = event.message.entities[0]
                if isinstance(probable_mention, MessageEntityMentionName):
                    user_id = probable_mention.user_id
                    user_obj = await event.client.get_entity(user_id)
                    return user_obj, extra
            if isinstance(user, int) or user.startswith("@"):
                user_obj = await event.client.get_entity(user)
                return user_obj, extra
    except ValueError:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
                obj = partial(type, "user", ())
                user_obj = obj({"id": int(user), "first_name": user})
                return user_obj, extra
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        LOGS.error(str(e))
    try:
        extra = event.pattern_match.group(group)
        if event.is_private:
            user_obj = await event.get_chat()
            return user_obj, extra
        if event.reply_to_msg_id:
            prev_msg = await event.get_reply_message()
            if not prev_msg.from_id:
                return None, None
            user_obj = await event.client.get_entity(prev_msg.sender_id)
            return user_obj, extra
        if not args:
            return None, None
    except Exception as e:
        LOGS.error(str(e))
    return None, None
