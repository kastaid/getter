# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from secrets import choice
from textwrap import shorten
from cachetools import cached, LRUCache
from heroku3 import from_key
from telethon import events
from getter import (
    StartTime,
    __version__,
    __layer__,
    __license__,
    __copyright__,
    Root,
    LOOP,
    HELP,
    WORKER,
    CALLS,
    TESTER,
    DEVS,
    MAX_MESSAGE_LEN,
)
from getter.config import Var, TZ, HANDLER
from getter.core.app import App
from getter.core.constants import *
from getter.core.decorators import kasta_cmd
from getter.core.functions import (
    is_telegram_link,
    get_username,
    mentionuser,
    display_name,
    get_doc_mime,
    humanbool,
    get_user_status,
    get_user,
    parse_pre,
    strip_format,
    strip_emoji,
    humanbytes,
    time_formatter,
    get_random_hex,
    run_async,
    make_async,
    Runner,
    Searcher,
    Carbon,
)
from getter.core.property import get_blacklisted
from getter.core.wrappers import eor, eod, sod
from getter.logger import LOGS

hl = HANDLER

NOCHATS = {
    -1001699144606,
    -1001700971911,
}

DEFAULT_GCAST_BLACKLIST = {
    -1001699144606,  # @kastaot
    -1001700971911,  # @kastaup
    -1001596433756,  # @MFIChat
    -1001294181499,  # @userbotindo
    -1001387666944,  # @PyrogramChat
    -1001221450384,  # @pyrogramlounge
    -1001109500936,  # @TelethonChat
    -1001235155926,  # @RoseSupportChat
    -1001421589523,  # @tdspya
    -1001360494801,  # @OFIOpenChat
    -1001435671639,  # @xfichat
}

DEFAULT_GUCAST_BLACKLIST = {
    777000,  # Telegram
    4247000,  # @notoscam
    431415000,  # @BotSupport
    454000,  # @dmcatelegram
}

DEFAULT_SHELL_BLACKLIST = {
    "rm",
    "-delete",
    "unlink",
    "shred",
    "rsync",
    "sleep",
    "history",
    "dd",
    "chmod",
    "chown",
    "mkfs",
    "mkswap",
    "chroot",
    "fdisk",
    "poweroff",
    "shutdown",
    "reboot",
    "halt",
    "exec",
    "kill",
    "crontab",
    "perl",
    "while",
    ":()",
    "/dev",
    "sudo",
    "dpkg",
    "apt",
}

CARBON_PRESETS = [
    ("blackboard", "#6676BE"),
    ("material", "#829FAF"),
    ("monokai", "#9E9E9E"),
    ("night-owl", "#B96BFF"),
    ("nord", "#9AC5EF"),
    ("oceanic-next", "#8DB1C0"),
    ("one-light", "#2B66DF"),
    ("seti", "#ABB8C3"),
    ("shades-of-purple", "#736FCA"),
    ("synthwave-84", "#9C77D9"),
    ("solarized-light", "#BBBBBB"),
    ("twilight", "#F9EDD4"),
    ("verminal", "#BD10E0"),
    ("vscode", "#E1962F"),
    ("zenburn", "#B6A291"),
]

RAYSO_THEMES = (
    "breeze",
    "candy",
    "crimson",
    "falcon",
    "meadow",
    "midnight",
    "raindrop",
    "sunset",
)


def Heroku() -> None:
    _conn = None
    try:
        if Var.HEROKU_API and Var.HEROKU_APP_NAME:
            _conn = from_key(Var.HEROKU_API)
    except BaseException as err:
        LOGS.exception(err)
    return _conn


@cached(cache=LRUCache(maxsize=512))
def HerokuStack() -> str:
    try:
        heroku_conn = Heroku()
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
        stack = app.info.stack.name
    except BaseException:
        stack = "none"
    return stack


if HerokuStack() == "container" or not (Var.HEROKU_API or Var.HEROKU_APP_NAME):
    CHROME_BIN = "/usr/bin/google-chrome-stable"
    CHROME_DRIVER = "/usr/bin/chromedriver"
else:
    CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROME_DRIVER = "/app/.chromedriver/bin/chromedriver"
