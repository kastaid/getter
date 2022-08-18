# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import sys
from telethon.client.telegramclient import TelegramClient
from telethon.network.connection.tcpfull import ConnectionTcpFull
from telethon.sessions.string import StringSession


def BaseApp() -> TelegramClient:
    from .. import __version__, LOOP
    from ..config import Var
    from ..logger import LOGS
    from .property import do_not_remove_credit

    do_not_remove_credit()
    if Var.STRING_SESSION:
        if len(Var.STRING_SESSION) != 353:
            LOGS.error("STRING_SESSION wrong. Copy paste correctly! Quitting...")
            sys.exit(1)
        session = StringSession(Var.STRING_SESSION)
    else:
        LOGS.error("STRING_SESSION empty. Please filling! Quitting...")
        sys.exit(1)
    try:
        app = TelegramClient(
            session=session,
            api_id=Var.API_ID,
            api_hash=Var.API_HASH,
            loop=LOOP,
            app_version=__version__,
            connection=ConnectionTcpFull,
            connection_retries=None,
            auto_reconnect=True,
        )
        app.parse_mode = "markdown"
    except Exception as err:
        LOGS.exception("[APP] - {}".format(err))
        sys.exit(1)
    return app


App = BaseApp()
