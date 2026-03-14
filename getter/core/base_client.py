# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import importlib.util
import os
import random
import sys
from collections import UserList
from collections.abc import Coroutine
from inspect import getmembers
from platform import machine, version
from time import time
from typing import Any, NoReturn

from telethon.client.telegramclient import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    AuthKeyDuplicatedError,
    InvalidBufferError,
    PhoneNumberInvalidError,
)
from telethon.network.connection import ConnectionTcpAbridged
from telethon.sessions.abstract import Session
from telethon.sessions.string import CURRENT_VERSION, StringSession
from telethon.tl import functions as fun, types as typ

from getter import (
    LOOP,
    Root,
    StartTime,
    __version__,
)
from getter.config import (
    DEVS,
    INVITE_WORKER,
    TZ,
    Var,
    hl,
)
from getter.logger import LOG

from .db import sgvar
from .functions import display_name
from .helper import plugins_help
from .property import do_not_remove_credit, get_blacklisted
from .utils import time_formatter

PLUGIN_DIR = Root / "getter/plugins"
CUSTOM_PLUGIN_DIR = Root / "getter/plugins/custom"


class ReverseList(UserList):
    def __iter__(self):
        return reversed(self)


class KastaClient(TelegramClient):
    def __init__(
        self,
        session: str | Session,
        api_id: int | None = None,
        api_hash: str | None = None,
        bot_token: str | None = None,
        *args,
        **kwargs,
    ):
        self._dialogs = []
        self._plugins = {}
        self.log = LOG
        kwargs["api_id"] = api_id
        kwargs["api_hash"] = api_hash
        kwargs["connection"] = ConnectionTcpAbridged
        kwargs["request_retries"] = 3
        kwargs["connection_retries"] = 3
        kwargs["auto_reconnect"] = True
        kwargs["device_model"] = "Getter"
        kwargs["system_version"] = " ".join((version(), machine()))
        kwargs["app_version"] = __version__
        kwargs["loop"] = LOOP
        kwargs["entity_cache_limit"] = 1000
        super().__init__(session, *args, **kwargs)
        self.__class__.__module__ = "telethon.client.telegramclient"
        self._event_builders = ReverseList()
        self.run_in_loop(self.start_client(bot_token=bot_token))
        self.dc_id = self.session.dc_id

    def __repr__(self):
        return f"<Kasta.Client:\n self: {self.full_name}\n id: {self.uid}\n>"

    @property
    def __dict__(self) -> dict | None:
        if self.me:
            return self.me.to_dict()

    async def start_client(self, **kwargs) -> None:
        self.log.info("Trying to login...")
        do_not_remove_credit()
        try:
            await asyncio.sleep(random.uniform(3.5, 6.5))
            await self.start(**kwargs)
            if await self.is_bot():
                self.log.critical("Bot account detected. Bots are not supported — use a USER account (userbot).")
                sys.exit(1)

            cfg = await self(fun.help.GetConfigRequest())
            for opt in cfg.dc_options:
                if opt.ip_address == self.session.server_address:
                    if self.session.dc_id != opt.id:
                        self.log.warning(f"Fixed DC ID in session from {self.session.dc_id} to {opt.id}")
                    self.session.set_dc(opt.id, opt.ip_address, opt.port)
                    self.session.save()
                    break

            await asyncio.sleep(3)
            self.me = await self.get_me()
            self.me.phone = None
            me = self.full_name
            if self.uid not in DEVS:
                KASTA_BLACKLIST = await get_blacklisted(
                    url="https://raw.githubusercontent.com/kastaid/resources/main/kastablacklist.py",
                    attempts=6,
                    fallbacks=None,
                )
                if self.uid in KASTA_BLACKLIST:
                    self.log.error(f"({me} - {self.uid}) YOU ARE BLACKLISTED !!")
                    sys.exit(1)
            self.log.success(f"Logged in as {me} [{self.uid}]")
        except (ValueError, ApiIdInvalidError):
            self.log.critical("API_ID and API_HASH combination does not match, please re-check! Quitting...")
            sys.exit(1)
        except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
            self.log.critical("STRING_SESSION expired, please create new! Quitting...")
            sys.exit(1)
        except Exception as err:
            self.log.exception(f"[KastaClient] - {err}")
            sys.exit(1)

    async def start_pytgcalls(self) -> None:
        try:
            self.log.info("Start PyTgCalls...")
            from pytgcalls import PyTgCalls

            TgCall = PyTgCalls(self)
            await TgCall.start()
            Var.TGCALL = TgCall
            self.log.success("PyTgCalls Started.")
        except Exception as err:
            self.log.exception(f"[KastaClient:PyTgCalls] - {err}")

    def run_in_loop(self, func: Coroutine[Any, Any, None]) -> Any:
        return self.loop.run_until_complete(func)

    def run(self) -> NoReturn:
        try:
            self.run_until_disconnected()
        except InvalidBufferError as err:
            self.log.exception(err)
            self.log.error("Client was stopped, restarting...")
            try:
                import psutil

                proc = psutil.Process(os.getpid())
                for p in proc.open_files() + proc.connections():
                    os.close(p.fd)
            except BaseException:
                pass
            os.execl(sys.executable, sys.executable, "-m", "getter")

    def add_handler(
        self,
        func: asyncio.Future,
        *args,
        **kwargs,
    ) -> None:
        if any(func is i[0] for i in self.list_event_handlers()):
            return
        self.add_event_handler(func, *args, **kwargs)

    async def reboot(
        self,
        message: typ.Message,
    ) -> NoReturn:
        try:
            chat_id = message.chat_id or message.from_id
            await sgvar("_reboot", f"{chat_id}|{message.id}")
        except BaseException:
            pass
        try:
            import psutil

            proc = psutil.Process(os.getpid())
            for p in proc.open_files() + proc.connections():
                os.close(p.fd)
        except BaseException:
            pass
        os.execl(sys.executable, sys.executable, "-m", "getter")

    def load_plugin(
        self,
        plugin: str,
    ) -> bool:
        try:
            path = CUSTOM_PLUGIN_DIR / plugin
            plug = path.stem
            name = f"getter.plugins.custom.{plug}"
            sys.modules.pop(name, None)
            spec = importlib.util.spec_from_file_location(name, path)
            if not spec or not spec.loader:
                raise ImportError(f"Cannot load plugin spec: {plugin}")
            mod = importlib.util.module_from_spec(spec)
            mod.Var = Var
            mod.tz = TZ
            mod.hl = hl
            mod.INVITE_WORKER = INVITE_WORKER
            mod.DEVS = DEVS
            mod.plugins_help = plugins_help
            spec.loader.exec_module(mod)
            self._plugins[plug] = mod
            return True
        except Exception as err:
            self.log.exception(err)
            return False

    def unload_plugin(
        self,
        plugin: str,
    ) -> None:
        mod = self._plugins.get(plugin)
        if not mod:
            return
        name = mod.__name__
        self._event_builders = ReverseList([eb for eb in self._event_builders if eb[1].__module__ != name])
        sys.modules.pop(name, None)
        del self._plugins[plugin]

    @property
    def all_plugins(self) -> list[dict[str, str]]:
        return [
            {
                "path": ".".join(p.with_suffix("").parts[-2:]),
                "name": p.stem,
            }
            for p in PLUGIN_DIR.rglob("*.py")
            if not p.name.endswith(("__.py", "_draft.py"))
        ]

    @property
    def full_name(self) -> str:
        return display_name(self.me)

    @property
    def uid(self) -> int:
        return self.me.id

    @property
    def uptime(self) -> str:
        return time_formatter(time() - StartTime)

    def to_dict(self) -> dict:
        return dict(getmembers(self))


_ssn = Var.STRING_SESSION
if _ssn:
    if _ssn.startswith(CURRENT_VERSION) and len(_ssn) != 353:
        LOG.critical("STRING_SESSION wrong. Copy paste correctly! Quitting...")
        sys.exit(1)
    session = StringSession(_ssn)
else:
    LOG.critical("STRING_SESSION empty. Please filling! Quitting...")
    sys.exit(1)

getter_app = KastaClient(
    session=session,
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
)
