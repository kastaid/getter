# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import re
from functools import partial, wraps
from io import BytesIO
from typing import Union, Tuple
from uuid import uuid4
from aiofiles import open as aiopen
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from emoji import replace_emoji
from markdown import markdown
from telethon.tl.types import (
    MessageEntityMentionName,
    MessageEntityPre,
    User,
    UserStatusOnline,
    UserStatusOffline,
    UserStatusLastWeek,
    UserStatusLastMonth,
    UserStatusRecently,
)
from telethon.utils import add_surrogate, get_display_name
from getter import LOOP, EXECUTOR
from getter.logger import LOGS


def is_telegram_link(url: str) -> bool:
    tlink_re = r"^(?:https?://)?((www)\.|)(?:t\.me|telegram\.(?:dog|me))/(\w+)$"
    return bool(re.match(tlink_re, url, flags=re.I))


def get_username(url: str) -> str:
    tusername_re = r"^(?:https?://)((www)\.|)(?:t\.me|telegram\.(?:dog|me))/"
    return re.sub(tusername_re, "@", url, flags=re.I)


def mentionuser(
    user_id: Union[int, str],
    name: str,
    sep: str = "",
    html: bool = False,
) -> str:
    if html:
        return f"<a href=tg://user?id={user_id}>{sep}{name}</a>"
    return f"[{sep}{name}](tg://user?id={user_id})"


def display_name(user) -> str:
    name = get_display_name(user)
    return name if name else "{}".format(user.first_name or "none")


def get_doc_mime(media) -> str:
    media_type = str((str(media)).split("(", maxsplit=1)[0])
    if media_type == "MessageMediaDocument":
        return media.document.mime_type
    return ""


def humanbool(b) -> str:
    return "No" if str(b).lower() in ("false", "none", "0", "") else "Yes"


def get_user_status(user: User) -> str:
    if user.bot or user.support:
        status = "none"
    if isinstance(user.status, UserStatusOnline):
        status = "online"
    elif isinstance(user.status, UserStatusOffline):
        status = "offline"
    elif isinstance(user.status, UserStatusRecently):
        status = "recently"
    elif isinstance(user.status, UserStatusLastWeek):
        status = "within_week"
    elif isinstance(user.status, UserStatusLastMonth):
        status = "within_month"
    else:
        status = "long_time_ago"
    return status


async def get_user(kst, group=1):
    args = kst.pattern_match.group(group).split(" ", 1)
    extra = None
    await kst.get_chat()
    try:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
                user = int(user)
            if kst.message.entities:
                mention = kst.message.entities[0]
                if isinstance(mention, MessageEntityMentionName):
                    user_id = mention.user_id
                    user_obj = await kst.client.get_entity(user_id)
                    return user_obj, extra
            if isinstance(user, int) or user.startswith("@"):
                user_obj = await kst.client.get_entity(user)
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
            return None, None
        else:
            return None, None
    except Exception as err:
        LOGS.error(str(err))
    try:
        extra = kst.pattern_match.group(group)
        if kst.is_private:
            user_obj = await kst.get_chat()
            return user_obj, extra
        if kst.is_reply:
            user_id = (await kst.get_reply_message()).sender_id
            try:
                user_obj = await kst.client.get_entity(user_id)
                return user_obj, extra
            except ValueError:
                obj = partial(type, "user", ())
                user_obj = obj({"id": user_id, "first_name": str(user_id)})
                return user_obj, extra
        if not args:
            return None, None
    except Exception as err:
        LOGS.error(str(err))
    return None, None


def parse_pre(text: str) -> str:
    text = text.strip()
    return (
        text,
        [MessageEntityPre(offset=0, length=len(add_surrogate(text)), language="")],
    )


def strip_format(md: str) -> str:
    html = markdown(md)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text().replace("```", "").strip()


def strip_emoji(text: str) -> str:
    return replace_emoji(text, "")


def humanbytes(size: Union[int, float]) -> str:
    if not size:
        return "0 B"
    power = 1024
    for _ in ("", "Ki", "Mi", "Gi", "Ti"):
        if size < power:
            break
        size /= power
    if isinstance(size, int):
        size = f"{size} {_}B"
    elif isinstance(size, float):
        size = f"{size:.2f} {_}B"
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
    return "0s"


def get_random_hex(chars: int = 12) -> str:
    return uuid4().hex[:chars]


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(  # noqa: C404
            [
                (key, todict(val, classkey))
                for key, val in obj.__dict__.items()
                if not callable(val) and not key.startswith("_")
            ]
        )
        if classkey and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    return obj


async def run_async(func, *args, **kwargs):
    return await LOOP.run_in_executor(executor=EXECUTOR, func=partial(func, *args, **kwargs))


def make_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_async(func, *args, **kwargs)

    return wrapper


async def Runner(cmd: str) -> Tuple[str, str, int, int]:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return (out, err, proc.returncode, proc.pid)


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
    *args,
    **kwargs,
):
    async with ClientSession(headers=headers) as session:
        try:
            if post:
                resp = await session.post(
                    url=url,
                    json=json,
                    data=data,
                    ssl=ssl,
                    raise_for_status=True,
                    *args,
                    **kwargs,
                )
            else:
                resp = await session.get(
                    url=url,
                    params=params,
                    ssl=ssl,
                    raise_for_status=True,
                    *args,
                    **kwargs,
                )
        except asyncio.TimeoutError:
            return None
        if resp.status not in (
            200,
            201,
        ):
            return None
        if re_json:
            return await resp.json(content_type=None)
        if re_content:
            return await resp.read()
        if real:
            return resp
        return await resp.text()


async def Carbon(
    code,
    url="https://carbonara-42.herokuapp.com/api/cook",  # https://carbonara.vercel.app/api/cook
    file_name="carbon",
    download=False,
    rayso=False,
    **kwargs,
):
    if rayso:
        url = "https://raysoapi.herokuapp.com/generate"
        kwargs["text"] = code
        kwargs["theme"] = kwargs.get("theme", "raindrop")
        kwargs["darkMode"] = kwargs.get("darkMode", True)
        kwargs["title"] = kwargs.get("title", "getter")
    else:
        kwargs["code"] = code
    res = await Searcher(
        url=url,
        post=True,
        json=kwargs,
        re_content=True,
    )
    if not res:
        return None
    file_name = f"{file_name}_{get_random_hex()}.jpg"
    if not download:
        file = BytesIO(res)
        file.name = file_name
    else:
        file = file_name
        async with aiopen(file, mode="wb") as f:
            await f.write(res)
    return file
