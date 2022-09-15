# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import re
import time
import typing
from functools import reduce
from math import ceil
from uuid import uuid4
from bs4 import BeautifulSoup
from cachetools import cached
from emoji import replace_emoji
from markdown import markdown


def humanbool(b: typing.Any, toggle: bool = False) -> str:
    return ("off" if toggle else "no") if str(b).lower() in ("false", "none", "0", "") else ("on" if toggle else "yes")


def replace_all(
    text: str,
    repls: dict,
    regex: bool = False,
) -> str:
    if regex:
        return reduce(lambda a, kv: re.sub(*kv, a, flags=re.I), repls.items(), text)
    return reduce(lambda a, kv: a.replace(*kv), repls.items(), text)


@cached(cache={})
def md_to_html(text: str) -> str:
    repls = {
        "<p>(.*)</p>": "\\1",
        r"\=\=(.*)\=\=": "<u>\\1</u>",
        r"\~\~(.*)\~\~": "<del>\\1</del>",
        r"\-\-(.*)\-\-": "<u>\\1</u>",
        r"\_\_(.*)\_\_": "<em>\\1</em>",
        r"\|\|(.*)\|\|": "<spoiler>\\1</spoiler>",
    }
    return replace_all(markdown(text), repls, regex=True)


@cached(cache={})
def strip_format(text: str) -> str:
    repls = {
        "==": "",
        "~~": "",
        "--": "",
        "__": "",
        "||": "",
    }
    return replace_all(BeautifulSoup(markdown(text), features="html.parser").get_text(), repls).strip()


@cached(cache={})
def strip_emoji(text: str) -> str:
    return replace_emoji(text, "").strip()


def strip_ascii(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def chunk(lst: list, size: int = 2) -> list:
    return [lst[_ * size : _ * size + size] for _ in list(range(ceil(len(lst) / size)))]


def sort_dict(dct: dict, reverse: bool = False) -> dict:
    return dict(sorted(dct.items(), reverse=reverse))


def humanbytes(size: typing.Union[int, float]) -> str:
    if not size:
        return "0 B"
    power = 1024
    pos = 0
    power_dict = {
        0: "",
        1: "K",
        2: "M",
        3: "G",
        4: "T",
        5: "P",
        6: "E",
        7: "Z",
        8: "Y",
    }
    while size > power:
        size /= power
        pos += 1
    return "{:.2f}{}B".format(size, power_dict[pos])


def time_formatter(ms) -> str:
    minutes, seconds = divmod(int(ms / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w, ") if weeks else "")
        + ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp and tmp[:-2] or "0s"


def until_time(
    timing: typing.Union[str, int],
    unit: str = "m",
) -> typing.Tuple[float, str]:
    if unit.lower() not in (
        "s",
        "m",
        "h",
        "d",
        "w",
    ):
        unit = "m"
    if not str(timing).isdecimal():
        raise TypeError("'timing' must be integers or str digits")
    if unit == "s":
        until = int(time.time() + int(timing) * 1)
        dur = "seconds"
    elif unit == "m":
        until = int(time.time() + int(timing) * 60)
        dur = "minutes"
    elif unit == "h":
        until = int(time.time() + int(timing) * 60 * 60)
        dur = "hours"
    elif unit == "d":
        until = int(time.time() + int(timing) * 24 * 60 * 60)
        dur = "days"
    else:
        until = int(time.time() + int(timing) * 7 * 24 * 60 * 60)
        dur = "weeks"
    return until, dur


def get_random_hex(chars: int = 12) -> str:
    return uuid4().hex[:chars]


def mask_email(email: str) -> str:
    at = email.find("@")
    return email[0] + "*" * int(at - 2) + email[at - 1 :]


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
        data = dict(  # noqa
            (key, todict(val, classkey))
            for key, val in obj.__dict__.items()
            if not callable(val) and not key.startswith("_")
        )
        if classkey and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    return obj


def camel(s: str) -> str:
    s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return "".join([s[0].lower(), s[1:]])


def snake(s: str) -> str:
    return "_".join(re.sub("([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))).split()).lower()


def kebab(s: str) -> str:
    return "-".join(
        re.sub(
            r"(\s|_|-)+",
            " ",
            re.sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda x: " " + x.group(0).lower(),
                s,
            ),
        ).split()
    )
