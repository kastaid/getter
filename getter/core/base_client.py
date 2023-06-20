# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import inspect
import os
import sys
import typing
from logging import Logger
from random import choice
from time import time
from telethon.client.telegramclient import TelegramClient
from telethon.errors.rpcerrorlist import (
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
    PhoneNumberInvalidError,
    AccessTokenExpiredError,
    AccessTokenInvalidError,
)
from telethon.network.connection.tcpfull import ConnectionTcpFull
from telethon.sessions.abstract import Session
from telethon.sessions.string import CURRENT_VERSION, StringSession
from telethon.tl import functions as fun, types as typ
from .. import StartTime, __version__, LOOP
from ..config import Var, DEVS
from ..logger import LOGS, TelethonLogger
from .db import sgvar
from .functions import display_name
from .property import do_not_remove_credit, get_blacklisted
from .utils import time_formatter


class KastaClient(TelegramClient):
    def __init__(
        self,
        session: typing.Union[str, Session],
        api_id: typing.Optional[int] = None,
        api_hash: typing.Optional[str] = None,
        bot_token: typing.Optional[str] = None,
        logs: Logger = LOGS,
        *args,
        **kwargs,
    ):
        self._dialogs = []
        self.logs = logs
        kwargs["api_id"] = api_id
        kwargs["api_hash"] = api_hash
        kwargs["base_logger"] = TelethonLogger
        kwargs["connection"] = ConnectionTcpFull
        kwargs["connection_retries"] = None
        kwargs["auto_reconnect"] = True
        super().__init__(session, **kwargs)
        self.run_in_loop(self.start_client(bot_token=bot_token))
        self.dc_id = self.session.dc_id

    def __repr__(self):
        return "<Kasta.Client:\n self: {}\n id: {}\n bot: {}\n>".format(
            self.full_name,
            self.uid,
            self._bot,
        )

    @property
    def __dict__(self) -> typing.Optional[dict]:
        if self.me:
            return self.me.to_dict()

    async def start_client(self, **kwargs) -> None:
        self.logs.info("Trying to login.")
        do_not_remove_credit()
        await asyncio.sleep(choice((1, 2, 3)))
        try:
            await self.start(**kwargs)
            self._bot = await self.is_bot()
            if not self._bot:
                cfg = await self(fun.help.GetConfigRequest())
                for opt in cfg.dc_options:
                    if opt.ip_address == self.session.server_address:
                        if self.session.dc_id != opt.id:
                            self.logs.warning(f"Fixed DC ID in session from {self.session.dc_id} to {opt.id}")
                        self.session.set_dc(opt.id, opt.ip_address, opt.port)
                        self.session.save()
                        break
            await asyncio.sleep(3)
            self.me = await self.get_me()
            if self.me.bot:
                me = f"@{self.me.username}"
            else:
                self.me.phone = None
                me = self.full_name
            await asyncio.sleep(3)
            if self.uid not in DEVS:
                KASTA_BLACKLIST = await get_blacklisted(
                    url="https://raw.githubusercontent.com/kastaid/resources/main/kastablacklist.py",
                    attempts=6,
                    fallbacks=None,
                )
                if self.uid in KASTA_BLACKLIST:
                    self.logs.error(
                        "({} - {}) YOU ARE BLACKLISTED !!".format(
                            me,
                            self.uid,
                        )
                    )
                    sys.exit(1)
            self.logs.success(
                "Logged in as {} [{}]".format(
                    me,
                    self.uid,
                )
            )
        except (ValueError, ApiIdInvalidError):
            self.logs.critical("API_ID and API_HASH combination does not match, please re-check! Quitting...")
            sys.exit(1)
        except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
            self.logs.critical("STRING_SESSION expired, please create new! Quitting...")
            sys.exit(1)
        except (AccessTokenExpiredError, AccessTokenInvalidError):
            self.logs.critical(
                "Bot Token expired or invalid. Create new from @Botfather and update BOT_TOKEN in Config Vars!"
            )
            sys.exit(1)
        except Exception as err:
            self.logs.exception(f"[KastaClient] - {err}")
            sys.exit(1)

    def run_in_loop(self, func: typing.Coroutine[typing.Any, typing.Any, None]) -> typing.Any:
        return self.loop.run_until_complete(func)

    def run(self) -> typing.NoReturn:
        self.run_until_disconnected()

    def add_handler(
        self,
        func: asyncio.Future,
        *args,
        **kwargs,
    ) -> None:
        if func in [_[0] for _ in self.list_event_handlers()]:
            return
        self.add_event_handler(func, *args, **kwargs)

    def reboot(self, message: typ.Message) -> typing.NoReturn:
        try:
            chat_id = message.chat_id or message.from_id
            sgvar("_reboot", f"{chat_id}|{message.id}")
        except BaseException:
            pass
        try:
            import psutil

            proc = psutil.Process(os.getpid())
            for _ in proc.open_files() + proc.connections():
                os.close(_.fd)
        except BaseException:
            pass
        os.execl(sys.executable, sys.executable, "-m", "getter")

    @property
    def full_name(self) -> str:
        return display_name(self.me)

    @property
    def uid(self) -> int:
        return self.me.id

    @property
    def uptime(self) -> str:
        return time_formatter((time() - StartTime) * 1000)

    def to_dict(self) -> dict:
        return dict(inspect.getmembers(self))


_ssn = Var.STRING_SESSION
if _ssn:
    if _ssn.startswith(CURRENT_VERSION) and len(_ssn) != 353:
        LOGS.critical("STRING_SESSION wrong. Copy paste correctly! Quitting...")
        sys.exit(1)
    session = StringSession(_ssn)
else:
    LOGS.critical("STRING_SESSION empty. Please filling! Quitting...")
    sys.exit(1)

getter_app = KastaClient(
    session=session,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    loop=LOOP,
    app_version=__version__,
    device_model="Getter",
)
