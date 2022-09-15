# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from contextlib import suppress
from random import choice
from telethon import events
from validators.url import url as is_url
from getter import (
    __layer__,
    __tlversion__,
    __version__,
    StartTime,
    __license__,
    __copyright__,
    __pyversion__,
    Root,
)
from getter.config import *
from getter.core import *
from getter.logger import LOGS

BOTLOGS = get_botlogs()  # cool yeah?

DEFAULT_GCAST_BLACKLIST = (
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
)

DEFAULT_GUCAST_BLACKLIST = (
    777000,  # Telegram
    4247000,  # @notoscam
    431415000,  # @BotSupport
    454000,  # @dmcatelegram
)

DEFAULT_SHELL_BLACKLIST = (
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
    "pkill",
)
