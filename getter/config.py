# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from os import getenv
from dotenv import find_dotenv, load_dotenv
from pytz import timezone, UnknownTimeZoneError
from getter.logger import LOGS

load_dotenv(find_dotenv("config.env"))


def tobool(val):
    """
    Convert a string representation of truth to true (1) or false (0).
    https://github.com/python/cpython/blob/main/Lib/distutils/util.py
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


class Var:
    DEV_MODE: bool = tobool(getenv("DEV_MODE", default="false").strip())
    STRING_SESSION: str = getenv("STRING_SESSION", default="").strip()
    API_ID: int = int(getenv("API_ID", default="0").strip())
    API_HASH: str = getenv("API_HASH", default="").strip()
    HANDLER: str = getenv("HANDLER", default=".").strip()
    TZ: str = getenv("TZ", default="Asia/Jakarta").strip()
    HEROKU_APP_NAME: str = getenv("HEROKU_APP_NAME", default="").strip()
    HEROKU_API: str = getenv("HEROKU_API", default="").strip()


try:
    TZ = timezone(Var.TZ)
except UnknownTimeZoneError:
    TZ = "Asia/Jakarta"
    LOGS.warning("Unknown TZ : {}".format(Var.TZ))
    LOGS.info("Set default TZ as {}".format(TZ))

if not (
    Var.HANDLER.startswith(
        (
            "/",
            ".",
            "!",
            "+",
            "-",
            "_",
            ";",
            "$",
            ",",
            "~",
            "^",
            "%",
            "&",
        )
    )
):
    HANDLER = "."
    LOGS.warning("Your HANDLER [{}] is not supported.".format(Var.HANDLER))
    LOGS.info("Set default HANDLER as dot [.command]")
else:
    HANDLER = "".join(Var.HANDLER.split())
