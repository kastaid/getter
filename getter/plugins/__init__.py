# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from telethon import events
from getter import (
    StartTime,
    __version__,
    Root,
    LOOP,
    HELP,
    WORKER,
    DEVS,
    NOCHATS,
)
from getter.app import App
from getter.config import Var, TZ, HANDLER
from getter.decorators import kasta_cmd
from getter.logger import LOGS
from getter.utils import (
    display_name,
    get_user,
    get_username,
    parse_pre,
    md_to_text,
    deEmojify,
    humanbytes,
    is_telegram_link,
    time_formatter,
    Runner,
    Searcher,
)
from getter.wrappers import eod, eor, eos

hl = HANDLER
