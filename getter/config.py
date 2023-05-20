# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import typing
from base64 import b64decode
from os import getenv
from string import ascii_lowercase
import dotenv
from pytz import timezone

dotenv.load_dotenv(dotenv.find_dotenv("config.env"))


def tobool(val: str) -> typing.Optional[int]:
    """
    Convert a string representation of truth to true (1) or false (0).
    https://github.com/python/cpython/blob/main/Lib/distutils/util.py
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    raise ValueError("invalid truth value %r" % (val,))


class Var:
    DEV_MODE: bool = tobool(getenv("DEV_MODE", "false").strip())
    API_ID: int = int(getenv("API_ID", "0").strip())
    API_HASH: str = getenv("API_HASH", "").strip()
    STRING_SESSION: str = getenv("STRING_SESSION", "").strip()
    DATABASE_URL: str = getenv("DATABASE_URL", "sqlite:///./getter.db").strip()
    BOTLOGS: int = int(getenv("BOTLOGS", "0").strip())
    HANDLER: str = getenv("HANDLER", ".").strip()
    NO_HANDLER: bool = tobool(getenv("NO_HANDLER", "false").strip())
    TZ: str = getenv("TZ", "Asia/Jakarta").strip()
    LANG_CODE: str = getenv("LANG_CODE", "id").lower().strip()
    HEROKU_APP_NAME: str = getenv("HEROKU_APP_NAME", "").strip()
    HEROKU_API: str = getenv("HEROKU_API", "").strip()


try:
    tz = timezone(Var.TZ)
except BaseException:
    _ = "Asia/Jakarta"
    print("An error or unknown TZ :", Var.TZ)
    print("Set default TZ as", _)
    tz = timezone(_)

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
    print("Your HANDLER [ {} ] is not supported.".format(Var.HANDLER))
    print("Set default HANDLER as dot [ .command ]")
else:
    hl = "".join(Var.HANDLER.split())

BOTLOGS_CACHE: typing.Set[int] = set()
DEV_CMDS: typing.Dict[str, typing.List[str]] = {}
SUDO_CMDS: typing.Dict[str, typing.List[str]] = {}
INVITE_WORKER: typing.Dict[str, typing.Any] = {}
CALLS: typing.Dict[int, typing.Any] = {}
TESTER = {5215824623}
# vo, en, xl
DEVS = {
    *{int(_) for _ in b64decode("MjAwMzM2MTQxMCAxOTk4OTE4MDI0IDE0MTU5NzEwMjA=").split()},
    *TESTER,
}
NOCHATS = {
    -1001699144606,
    -1001700971911,
}
del typing, b64decode, ascii_lowercase, dotenv, timezone
