# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
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
