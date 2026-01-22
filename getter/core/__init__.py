# ruff: noqa: F401, F403
# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from .base_client import getter_app
from .constants import *
from .db import *
from .decorators import kasta_cmd, sendlog
from .functions import (
    MSG_ID_RE,
    TELEGRAM_LINK_RE,
    USERNAME_RE,
    admin_check,
    display_name,
    get_chat_id,
    get_media_type,
    get_msg_id,
    get_text,
    get_user,
    get_user_status,
    get_username,
    is_admin,
    is_telegram_link,
    mentionuser,
    normalize_chat_id,
    parse_pre,
    to_privilege,
)
from .helper import (
    formatx_send,
    from_key,
    get_botlogs,
    hk,
    jdata,
    plugins_help,
)
from .patched import *
from .patcher import patch, patchable
from .property import do_not_remove_credit, get_blacklisted
from .tools import (
    Carbon,
    Fetch,
    MyIp,
    Pinger,
    Runner,
    Screenshot,
    Telegraph,
    aioify,
    import_lib,
    is_termux,
)
from .utils import (
    camel,
    chunk,
    deep_get,
    get_full_class_name,
    get_random_alpha,
    get_random_hex,
    humanbool,
    humanbytes,
    kebab,
    mask_email,
    md_to_html,
    normalize,
    replace_all,
    snake,
    sort_dict,
    strip_ascii,
    strip_emoji,
    strip_format,
    time_formatter,
    to_dict,
    until_time,
)

if hk.stack == "container" or not hk.is_heroku:
    CHROME_BIN = "/usr/bin/google-chrome"
    CHROME_DRIVER = "/usr/bin/chromedriver"
else:
    CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROME_DRIVER = "/app/.chromedriver/bin/chromedriver"
