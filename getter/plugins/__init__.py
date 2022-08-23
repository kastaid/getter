# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from contextlib import suppress
from random import choice
from textwrap import shorten
from validators.url import url as is_url
from getter import (
    StartTime,
    __license__,
    __copyright__,
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
    Root,
    LOOP,
    WORKER,
    CALLS,
    TESTER,
    DEVS,
    MAX_MESSAGE_LEN,
)
from getter.config import Var, TZ, HANDLER
from getter.core import *
from getter.logger import LOGS

hl = HANDLER

NOCHATS = {
    -1001699144606,
    -1001700971911,
    -1001261461928,
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
    -1001275084637,  # @OFIChat
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
    ("blackboard", "#6676be"),
    ("material", "#829faf"),
    ("monokai", "#9e9e9e"),
    ("night-owl", "#b96bff"),
    ("nord", "#9ac5ef"),
    ("oceanic-next", "#8db1c0"),
    ("one-light", "#2b66df"),
    ("seti", "#abb8c3"),
    ("shades-of-purple", "#736fca"),
    ("synthwave-84", "#9c77d9"),
    ("solarized-light", "#bbbbbb"),
    ("twilight", "#f9edd4"),
    ("verminal", "#bd10e0"),
    ("vscode", "#e1962f"),
    ("zenburn", "#b6a291"),
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

USERAGENTS = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) "
    "Chrome/19.0.1084.46 Safari/536.5",
    "Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) " "Chrome/19.0.1084.46 Safari/536.5",
    "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
)
