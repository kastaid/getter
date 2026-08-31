# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import math
import random
import re
import unicodedata
from functools import reduce
from string import ascii_letters
from time import time
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

import cachebox
from emoji import replace_emoji
from telethon.extensions import html, markdown

_BYTE_UNITS = ("", "K", "M", "G", "T")
_TIME_UNITS = {
    "s": (1, "seconds"),
    "m": (60, "minutes"),
    "h": (3600, "hours"),
    "d": (86400, "days"),
    "w": (604800, "weeks"),
}


def format_bytes(size: float) -> str:
    if size <= 0:
        return "0 B"
    mag = min(int(math.log(size, 1024)), len(_BYTE_UNITS) - 1)
    unit = _BYTE_UNITS[mag]
    scaled = round(size / (1024**mag), 1)
    if scaled.is_integer():
        scaled = int(scaled)
    return f"{scaled} {unit}B"


def format_time(
    elapsed: float,
    readable: bool = False,
    short: bool = False,
) -> str:
    total = int(elapsed)
    ms = int((elapsed - total) * 1000)
    sec = total % 60
    total //= 60
    mins = total % 60
    total //= 60
    hour = total % 24
    total //= 24
    day = total % 30
    total //= 30
    month = total % 12
    year = total // 12
    week = day // 7
    day %= 7
    if short:
        if year:
            day = hour = mins = sec = ms = 0
        elif week:
            mins = sec = ms = 0
        elif day:
            sec = ms = 0
        elif hour or sec:
            ms = 0
    if not (year or month or week or day or hour or mins or sec or ms):
        return "0 seconds" if readable else "0s"
    p = []
    if readable:
        if year:
            p.append(f"{year} year{'s' if year > 1 else ''}")
        if month:
            p.append(f"{month} month{'s' if month > 1 else ''}")
        if week:
            p.append(f"{week} week{'s' if week > 1 else ''}")
        if day:
            p.append(f"{day} day{'s' if day > 1 else ''}")
        if hour:
            p.append(f"{hour} hour{'s' if hour > 1 else ''}")
        if mins:
            p.append(f"{mins} minute{'s' if mins > 1 else ''}")
        if sec:
            p.append(f"{sec} second{'s' if sec > 1 else ''}")
        if ms:
            p.append(f"{ms} millisecond{'s' if ms > 1 else ''}")
    else:
        if year:
            p.append(f"{year}y")
        if month:
            p.append(f"{month}mo")
        if week:
            p.append(f"{week}w")
        if day:
            p.append(f"{day}d")
        if hour:
            p.append(f"{hour}h")
        if mins:
            p.append(f"{mins}m")
        if sec:
            p.append(f"{sec}s")
        if ms:
            p.append(f"{ms}ms")
    return ", ".join(p)


def format_latency(elapsed: float) -> str:
    return f"{elapsed * 1000:.0f}ms" if elapsed < 0.1 else f"{elapsed:.2f}s"


def until_time(
    timing: str | int,
    unit: str = "m",
) -> tuple[int, str]:
    if not str(timing).isdecimal():
        raise TypeError("'timing' must be an integer or digit string")
    multiplier, duration = _TIME_UNITS.get(unit.lower(), _TIME_UNITS["m"])
    return int(time() + int(timing) * multiplier), duration


def humanbool(key: Any, toggle: bool = False) -> str:
    return (
        ("Off" if toggle else "No") if str(key).lower() in {"false", "none", "0", ""} else ("On" if toggle else "Yes")
    )


def replace_all(
    text: str,
    repls: dict,
    regex: bool = False,
) -> str:
    if regex:
        return reduce(lambda a, kv: re.sub(*kv, a, flags=re.IGNORECASE), repls.items(), text)
    return reduce(lambda a, kv: a.replace(*kv), repls.items(), text)


def md_to_html(text: str) -> str:
    text, entities = markdown.parse(text)
    return html.unparse(text, entities)


def strip_format(text: str) -> str:
    return markdown.parse(text)[0].strip()


def strip_emoji(text: str) -> str:
    return replace_emoji(text, "").strip()


def strip_ascii(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def get_random_hex(length: int = 12) -> str:
    return uuid4().hex[:length]


def get_random_alpha(length: int = 12) -> str:
    return "".join(random.choice(ascii_letters) for _ in range(length))


def mask_email(email: str) -> str:
    at = email.find("@")
    return email[0] + "*" * int(at - 2) + email[at - 1 :]


def chunk(items: list, limit: int = 2) -> list:
    return [items[i * limit : (i + 1) * limit] for i in range(len(items) // limit + (len(items) % limit > 0))]


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
    text = re.sub(r"[_-]+", " ", text).title().replace(" ", "")
    return "".join([text[:1].lower(), text[1:]])


def snake(text: str) -> str:
    text = text.replace("-", " ")
    text = re.sub(r"([A-Z]+)", r" \1", text)
    text = re.sub(r"([A-Z][a-z]+)", r" \1", text)
    return "_".join(text.split()).lower()


def kebab(text: str) -> str:
    text = re.sub(
        r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+", lambda i: " " + i.group(0).lower(), text
    )
    text = re.sub(r"[\s_-]+", " ", text)
    return "-".join(text.split())


@cachebox.cached({})
def normalize(text: str) -> str:
    return "".join(i for i in unicodedata.normalize("NFKD", text) if not unicodedata.combining(i))


def is_url(value: str) -> bool:
    if not isinstance(value, str) or not value or any(i.isspace() for i in value):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.hostname) and "." in parsed.hostname


def get_full_class_name(value: Any) -> str:
    cls = type(value)
    module = cls.__module__
    return cls.__name__ if module in {None, "builtins"} else f"{module}.{cls.__name__}"
