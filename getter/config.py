# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from base64 import b64decode
from os import getenv
from string import ascii_lowercase
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def tobool(val: str) -> int | None:
    """
    Convert a string representation of truth to true (1) or false (0).
    https://github.com/python/cpython/blob/main/Lib/distutils/util.py
    """
    val = val.lower()
    if val in {"y", "yes", "t", "true", "on", "1"}:
        return 1
    if val in {"n", "no", "f", "false", "off", "0"}:
        return 0
    raise ValueError(f"invalid truth value {val!r}")


class Var:
    DEV_MODE: bool = tobool(getenv("DEV_MODE", "false").strip())
    API_ID: int = int(getenv("API_ID", "0").strip())
    API_HASH: str = getenv("API_HASH", "").strip()
    STRING_SESSION: str = getenv("STRING_SESSION", "").strip()
    DATABASE_URL: str = (
        lambda c: (
            c.replace(c.split("://")[0], "postgresql+asyncpg") if c.startswith(("postgres:", "postgresql:")) else c
        )
    )(getenv("DATABASE_URL", "sqlite+aiosqlite:///./getter.db").strip())
    BOTLOGS: int = int(getenv("BOTLOGS", "0").strip())
    HANDLER: str = getenv("HANDLER", ".").strip()
    NO_HANDLER: bool = tobool(getenv("NO_HANDLER", "false").strip())
    TZ: str = getenv("TZ", "Asia/Jakarta").strip()
    LANG_CODE: str = getenv("LANG_CODE", "id").lower().strip()
    HEROKU_APP_NAME: str = getenv("HEROKU_APP_NAME", "").strip()
    HEROKU_API: str = getenv("HEROKU_API", "").strip()


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
CALLS: dict[int, Any] = {}
TESTER = {5215824623}
# va, en
DEVS = {*{int(_) for _ in b64decode("MjAwMzM2MTQxMCAxNzkyNDg2MTUw").split()}, *TESTER}
NOCHATS = {
    -1001699144606,
    -1001700971911,
}
del b64decode, ascii_lowercase, ZoneInfo, load_dotenv, find_dotenv
