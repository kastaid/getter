# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from base64 import b64decode
from os import getenv
from string import ascii_lowercase
from typing import Any, ClassVar
from zoneinfo import ZoneInfo

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


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
    _db = env("DATABASE_URL", "sqlite+aiosqlite:///./getter.db")
    DATABASE_URL = (
        _db.replace(_db.split("://")[0], "postgresql+asyncpg") if _db.startswith(("postgres:", "postgresql:")) else _db
    )
    BOTLOGS: int = int(env("BOTLOGS", "0"))
    HANDLER: str = env("HANDLER", ".")
    NO_HANDLER: bool = to_bool(env("NO_HANDLER", "false"))
    TZ: str = env("TZ", "Asia/Jakarta")
    LANG_CODE: str = env("LANG_CODE", "id").lower()
    HEROKU_APP_NAME: str = env("HEROKU_APP_NAME", "")
    HEROKU_API: str = env("HEROKU_API", "")
    TGCALL: Any = None
    CALLS: ClassVar[set[int]] = set()


try:
    TZ = ZoneInfo(Var.TZ)
except BaseException:
    _ = "Asia/Jakarta"
    print("An error or unknown TZ :", Var.TZ)
    print("Set default TZ as", _)
    TZ = ZoneInfo(_)

if not (
    Var.HANDLER.lower().startswith(
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
    )
):
    hl = "."
    print(f"Your HANDLER [ {Var.HANDLER} ] is not supported.")
    print("Set default HANDLER as dot [ .command ]")
else:
    hl = "".join(Var.HANDLER.split())

BOTLOGS_CACHE: list[int] = []
DEV_CMDS: dict[str, list[str]] = {}
SUDO_CMDS: dict[str, list[str]] = {}
INVITE_WORKER: dict[str, Any] = {}
TESTER = {5215824623}
# va, en
DEVS = {*{int(_) for _ in b64decode("MjAwMzM2MTQxMCAxNzkyNDg2MTUw").split()}, *TESTER}
NOCHATS = {
    -1001699144606,
    -1001700971911,
}
del b64decode, ascii_lowercase, ZoneInfo, load_dotenv, find_dotenv
