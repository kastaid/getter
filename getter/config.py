# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from base64 import b64decode
from os import getenv
from string import ascii_lowercase
from typing import ClassVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

from . import Root

load_dotenv(Root / ".env", override=True)


def to_bool(value: str) -> bool:
    value = value.lower()
    if value in {"y", "yes", "t", "true", "on", "1", "enable", "enabled"}:
        return True
    if value in {"n", "no", "f", "false", "off", "0", "disable", "disabled"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def env(key: str, default: str = "") -> str:
    return getenv(key, default).strip()


class Var:
    DEV_MODE: bool = to_bool(env("DEV_MODE", "false"))
    API_ID: int = int(env("API_ID", "0"))
    API_HASH: str = env("API_HASH", "")
    STRING_SESSION: str = env("STRING_SESSION", "")
    DATABASE_URL: str = env("DATABASE_URL", "sqlite+aiosqlite:///./getter.db")
    BOTLOGS: int = int(env("BOTLOGS", "0"))
    LANG_CODE: str = env("LANG_CODE", "id").lower()
    HEROKU_APP_NAME: str = env("HEROKU_APP_NAME", "")
    HEROKU_API: str = env("HEROKU_API", "")

    TIMEZONE: str = env("TIMEZONE", "Asia/Jakarta")
    try:
        TZ = ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError:
        TIMEZONE = "Asia/Jakarta"
        print("Unknown TIMEZONE, fallback to", TIMEZONE)
        TZ = ZoneInfo(TIMEZONE)

    HANDLER: str = env("HANDLER", ".")
    NO_HANDLER: bool = to_bool(env("NO_HANDLER", "false"))
    PREFIX = "" if NO_HANDLER else "".join(HANDLER.split())
    if PREFIX and not PREFIX.lower().startswith(
        (
            "/",
            ".",
            "!",
            "+",
            "-",
            "_",
            ";",
            "~",
            "^",
            "%",
            "&",
            ">",
            "<",
            *tuple(ascii_lowercase),
        ),
    ):
        PREFIX = "."
        print("Invalid HANDLER, fallback to", PREFIX)

    DEV_CMDS: ClassVar[dict[str, list[str]]] = {}
    SUDO_CMDS: ClassVar[dict[str, list[str]]] = {}
    DEVS: ClassVar[set[int]] = {int(i) for i in b64decode("MjAwMzM2MTQxMCAxNzkyNDg2MTUw").split()}
    NOCHATS: ClassVar[set[int]] = {-1004429397890}
