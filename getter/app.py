# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import sys
from telethon import TelegramClient
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession


def Client() -> TelegramClient:
    from getter import __version__
    from getter.config import Var
    from getter.logger import LOGS

    if Var.STRING_SESSION:
        if len(Var.STRING_SESSION) != 353:
            LOGS.error("STRING_SESSION wrong. Copy paste correctly! Quitting...")
            sys.exit(1)
        session = StringSession(Var.STRING_SESSION)
    else:
        LOGS.error("STRING_SESSION empty. Please filling! Quitting...")
        sys.exit(1)
    try:
        client = TelegramClient(
            session=session,
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            loop=None,
            app_version=__version__,
            connection=ConnectionTcpAbridged,
            auto_reconnect=True,
            connection_retries=None,
        )
        client.parse_mode = "markdown"
    except Exception as e:
        LOGS.exception("[APP] - {}".format(e))
        sys.exit(1)
    return client


App = Client()
