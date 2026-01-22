# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from functools import reduce
from math import ceil
from random import choice
from re import IGNORECASE, sub
from string import ascii_letters
from time import time
from typing import Any
from uuid import uuid4

from bs4 import BeautifulSoup
from cachetools import cached
from emoji import replace_emoji
from markdown.core import markdown
from unidecode import unidecode


def humanbool(b: Any, toggle: bool = False) -> str:
    return ("off" if toggle else "no") if str(b).lower() in {"false", "none", "0", ""} else ("on" if toggle else "yes")


def replace_all(
    text: str,
    repls: dict,
    regex: bool = False,
) -> str:
    if regex:
        return reduce(lambda a, kv: sub(*kv, a, flags=IGNORECASE), repls.items(), text)
    return reduce(lambda a, kv: a.replace(*kv), repls.items(), text)


def md_to_html(text: str) -> str:
    repls = {
        "<p>(.*)</p>": "\\1",
        r"\~\~(.*)\~\~": "<del>\\1</del>",
        r"\-\-(.*)\-\-": "<u>\\1</u>",
        r"\_\_(.*)\_\_": "<em>\\1</em>",
        r"\|\|(.*)\|\|": "<spoiler>\\1</spoiler>",
    }
    return replace_all(markdown(text), repls, regex=True)


def strip_format(text: str) -> str:
    repls = {
        "~~": "",
        "--": "",
        "__": "",
        "||": "",
    }
    return replace_all(BeautifulSoup(markdown(text), features="html.parser").get_text(), repls).strip()


def strip_emoji(text: str) -> str:
    return replace_emoji(text, "").strip()


def strip_ascii(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def humanbytes(size: int | float) -> str:
    if not size:
        return "0 B"
    power = 1024
    pos = 0
    power_dict = {0: "", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P", 6: "E", 7: "Z", 8: "Y"}
    while size > power:
        size /= power
        pos += 1
    return f"{size:.2f}{power_dict[pos]}B"


def time_formatter(ms: int | float) -> str:
    minutes, seconds = divmod(int(ms / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    time_units = (
        f"{weeks}w, " if weeks else "",
        f"{days}d, " if days else "",
        f"{hours}h, " if hours else "",
        f"{minutes}m, " if minutes else "",
        f"{seconds}s, " if seconds else "",
    )
    return "".join(time_units)[:-2] or "0s"


def until_time(
    timing: str | int,
    unit: str = "m",
) -> tuple[float, str]:
    if unit.lower() not in {
        "s",
        "m",
        "h",
        "d",
        "w",
    }:
        unit = "m"
    if not str(timing).isdecimal():
        raise TypeError("'timing' must be integers or str digits")
    if unit == "s":
        until = int(time() + int(timing) * 1)
        dur = "seconds"
    elif unit == "m":
        until = int(time() + int(timing) * 60)
        dur = "minutes"
    elif unit == "h":
        until = int(time() + int(timing) * 60 * 60)
        dur = "hours"
    elif unit == "d":
        until = int(time() + int(timing) * 24 * 60 * 60)
        dur = "days"
    else:
        until = int(time() + int(timing) * 7 * 24 * 60 * 60)
        dur = "weeks"
    return until, dur


def get_random_hex(length: int = 12) -> str:
    return uuid4().hex[:length]


def get_random_alpha(length: int = 12) -> str:
    return "".join(choice(ascii_letters) for _ in range(length))


def mask_email(email: str) -> str:
    at = email.find("@")
    return email[0] + "*" * int(at - 2) + email[at - 1 :]


def chunk(lst: list, size: int = 2) -> list:
    return [lst[_ * size : _ * size + size] for _ in list(range(ceil(len(lst) / size)))]


def sort_dict(dct: dict, reverse: bool = False) -> dict:
    return dict(sorted(dct.items(), reverse=reverse))


def deep_get(
    dct: dict,
    keys: str,
    default: Any = None,
) -> Any:
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dct)


def to_dict(
    obj: Any,
    classkey: str | None = None,
) -> Any:
    if isinstance(obj, dict):
        data = {}
        for k, v in obj.items():
            data[k] = to_dict(v, classkey)
        return data
    if hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    if hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(i, classkey) for i in obj]
    if hasattr(obj, "__dict__"):
        data = {k: to_dict(v, classkey) for k, v in obj.__dict__.items() if not callable(v) and not k.startswith("_")}
        if classkey and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    return obj


def camel(text: str) -> str:
    text = sub(r"(_|-)+", " ", text).title().replace(" ", "")
    return "".join([text[0].lower(), text[1:]])


def snake(text: str) -> str:
    return "_".join(sub(r"([A-Z][a-z]+)", r" \1", sub(r"([A-Z]+)", r" \1", text.replace("-", " "))).split()).lower()


def kebab(text: str) -> str:
    return "-".join(
        sub(
            r"(\s|_|-)+",
            " ",
            sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda x: " " + x.group(0).lower(),
                text,
            ),
        ).split()
    )


@cached(cache={})
def normalize(text: str) -> str:
    return unidecode(text)


def get_full_class_name(obj: Any) -> str:
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__
