# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import inspect
import sys
from contextlib import suppress
from logging import Logger
from random import choice
from typing import Union
from telethon import utils as telethon_utils
from telethon.client.telegramclient import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
    PhoneNumberInvalidError,
    AccessTokenExpiredError,
    AccessTokenInvalidError,
)
from telethon.network.connection.tcpfull import ConnectionTcpFull
from telethon.sessions.string import StringSession
from .. import DEVS, __version__, LOOP
from ..config import Var
from ..logger import LOGS
from .functions import display_name
from .property import do_not_remove_credit, get_blacklisted


class KastaClient(TelegramClient):
    def __init__(
        self,
        session,
        api_id=None,
        api_hash=None,
        bot_token=None,
        logger: Logger = LOGS,
        *args,
        **kwargs,
    ):
        self._dialogs = []
        self.logger = logger
        kwargs["api_id"] = api_id or Var.API_ID
        kwargs["api_hash"] = api_hash or Var.API_HASH
        kwargs["loop"] = LOOP
        kwargs["connection"] = ConnectionTcpFull
        kwargs["connection_retries"] = None
        kwargs["auto_reconnect"] = True
        super().__init__(session, **kwargs)
        self.run_in_loop(self.start_client(bot_token=bot_token))
        self.dc_id = self.session.dc_id

    def __repr__(self):
        return "<Kasta.Client:\n self: {} [{}]\n bot: {}\n>".format(self.full_name, self.uid, self._bot)

    @property
    def __dict__(self):
        if self.me:
            return self.me.to_dict()

    async def start_client(self, **kwargs):
        try:
            do_not_remove_credit()
            await asyncio.sleep(choice((4, 6, 8)))
            await self.start(**kwargs)
            await asyncio.sleep(5)
            self.me = await self.get_me()
            if self.me.bot:
                me = f"@{self.me.username}"
            else:
                self.me.phone = None
                me = self.full_name
            await asyncio.sleep(5)
            if self.uid not in DEVS:
                KASTA_BLACKLIST = await get_blacklisted(
                    url="https://raw.githubusercontent.com/kastaid/resources/main/kastablacklist.py",
                    attempts=6,
                    fallbacks=[],
                )
                if self.uid in KASTA_BLACKLIST:
                    self.logger.error(
                        "({} - {}) YOU ARE BLACKLISTED !!".format(
                            me,
                            self.uid,
                        )
                    )
                    sys.exit(1)
            self.logger.success(
                "Logged in as {} [{}]".format(
                    me,
                    self.uid,
                )
            )
        except (ValueError, ApiIdInvalidError):
            self.logger.critical("API_ID and API_HASH combination does not match, please re-check! Quitting...")
            sys.exit(1)
        except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
            self.logger.critical("STRING_SESSION expired, please create new! Quitting...")
            sys.exit(1)
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            self.logger.critical(
                "Bot Token expired or invalid. Create new from @Botfather and update BOT_TOKEN in Config Vars!"
            )
            sys.exit(1)
        except Exception as err:
            self.logger.exception("[KastaClient] - {}".format(err))
            sys.exit(1)

    def run_in_loop(self, function):
        return self.loop.run_until_complete(function)

    async def run(self):
        await self.run_until_disconnected()

    def add_handler(self, func, *args, **kwargs):
        if func in [_[0] for _ in self.list_event_handlers()]:
            return
        self.add_event_handler(func, *args, **kwargs)

    @property
    def utils(self):
        return telethon_utils

    @property
    def full_name(self) -> str:
        return display_name(self.me)

    @property
    def uid(self):
        return self.me.id

    def to_dict(self):
        return dict(inspect.getmembers(self))

    async def parse_id(self, text: Union[int, str]):
        with suppress(ValueError):
            text = int(text)
        return await self.get_peer_id(text)


if Var.STRING_SESSION:
    if len(Var.STRING_SESSION) != 353:
        LOGS.error("STRING_SESSION wrong. Copy paste correctly! Quitting...")
        sys.exit(1)
    session = StringSession(Var.STRING_SESSION)
else:
    LOGS.error("STRING_SESSION empty. Please filling! Quitting...")
    sys.exit(1)

getter_app = KastaClient(
    session,
    app_version=__version__,
    device_model="Getter",
)
