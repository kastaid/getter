# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .client import getter_app
from .constants import *
from .decorators import kasta_cmd
from .functions import (
    is_telegram_link,
    get_username,
    mentionuser,
    display_name,
    get_doc_mime,
    humanbool,
    get_user_status,
    get_user,
    get_chat_msg_id,
    parse_pre,
    replace_all,
    md_to_html,
    strip_format,
    strip_emoji,
    chunk,
    humanbytes,
    time_formatter,
    get_random_hex,
    mask_email,
    todict,
    run_async,
    make_async,
    Runner,
    Searcher,
    Carbon,
    Screenshot,
)
from .helper import plugins_help, from_key, Hk
from .property import get_blacklisted, do_not_remove_credit
from .wrappers import eor, eod, sod

if Hk.stack == "container" or not Hk.is_heroku:
    CHROME_BIN = "/usr/bin/google-chrome"
    CHROME_DRIVER = "/usr/bin/chromedriver"
else:
    CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROME_DRIVER = "/app/.chromedriver/bin/chromedriver"
