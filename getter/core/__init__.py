# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .client import getter_app
from .constants import *
from .db import *
from .decorators import kasta_cmd, sendlog
from .functions import (
    TELEGRAM_LINK_RE,
    USERNAME_RE,
    MSG_ID_RE,
    is_telegram_link,
    get_username,
    get_msg_id,
    mentionuser,
    display_name,
    normalize_chat_id,
    get_chat_id,
    get_text,
    get_user_status,
    get_user,
    is_admin,
    admin_check,
    to_privilege,
    parse_pre,
    get_media_type,
)
from .helper import (
    plugins_help,
    from_key,
    hk,
    jdata,
    get_botlogs,
)
from .property import get_blacklisted, do_not_remove_credit
from .tools import (
    aioify,
    import_lib,
    Runner,
    Fetch,
    Carbon,
    Screenshot,
    MyIp,
    Pinger,
    Telegraph,
)
from .utils import (
    humanbool,
    replace_all,
    md_to_html,
    strip_format,
    strip_emoji,
    strip_ascii,
    chunk,
    sort_dict,
    humanbytes,
    time_formatter,
    until_time,
    get_random_hex,
    mask_email,
    todict,
    camel,
    snake,
    kebab,
)
from .wrappers import (
    eor,
    eod,
    sod,
    try_delete,
)

if hk.stack == "container" or not hk.is_heroku:
    CHROME_BIN = "/usr/bin/google-chrome"
    CHROME_DRIVER = "/usr/bin/chromedriver"
else:
    CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROME_DRIVER = "/app/.chromedriver/bin/chromedriver"
