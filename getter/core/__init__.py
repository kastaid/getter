# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .base_client import getter_app
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
    format_exc,
)
from .patched import *
from .patcher import patch, patchable
from .property import get_blacklisted, do_not_remove_credit
from .tools import (
    is_termux,
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
    humanbytes,
    time_formatter,
    until_time,
    get_random_hex,
    get_random_alpha,
    mask_email,
    chunk,
    sort_dict,
    deep_get,
    to_dict,
    camel,
    snake,
    kebab,
    normalize,
    get_full_class_name,
)

if hk.stack == "container" or not hk.is_heroku:
    CHROME_BIN = "/usr/bin/google-chrome"
    CHROME_DRIVER = "/usr/bin/chromedriver"
else:
    CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROME_DRIVER = "/app/.chromedriver/bin/chromedriver"
