# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import inspect
import os
import sys
import time
import typing
from contextlib import suppress
from logging import Logger
from random import choice
from telethon import hints, utils
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
from .. import StartTime, __version__
from ..config import Var, DEVS
from ..logger import LOGS, TelethonLogger
from .db import sgvar
from .functions import (
    display_name,
    get_chat_id,
    get_text,
    get_user,
)
from .property import do_not_remove_credit, get_blacklisted
from .utils import time_formatter

delattr(fun.account, "DeleteAccountRequest")


class KastaClient(TelegramClient):
    def __init__(
        self,
        session: typing.Union[str, Session],
        api_id: typing.Optional[int] = None,
        api_hash: typing.Optional[str] = None,
        bot_token: typing.Optional[str] = None,
        logger: Logger = LOGS,
        *args,
        **kwargs,
    ):
        self._dialogs = []
        self.logger = logger
        kwargs["api_id"] = api_id or Var.API_ID
        kwargs["api_hash"] = api_hash or Var.API_HASH
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
        try:
            do_not_remove_credit()
            await asyncio.sleep(choice((4, 6, 8)))
            await self.start(**kwargs)
            if not self._bot:
                cfg = await self(fun.help.GetConfigRequest())
                for opt in cfg.dc_options:
                    if opt.ip_address == self.session.server_address:
                        if self.session.dc_id != opt.id:
                            self.logger.warning(f"Fixed DC ID in session from {self.session.dc_id} to {opt.id}")
                        self.session.set_dc(opt.id, opt.ip_address, opt.port)
                        self.session.save()
                        break
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
                    fallbacks=None,
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
            self.logger.exception(f"[KastaClient] - {err}")
            sys.exit(1)

    def run_in_loop(self, func: asyncio.Future) -> None:
        return self.loop.run_until_complete(func)

    def run(self) -> None:
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

    def reboot(self, message: typ.Message) -> None:
        with suppress(BaseException):
            sgvar("_reboot", f"{message.chat_id}|{message.id}")
        with suppress(BaseException):
            import psutil

            proc = psutil.Process(os.getpid())
            for _ in proc.open_files() + proc.connections():
                os.close(_.fd)
        os.execl(sys.executable, sys.executable, "-m", "getter")

    @property
    def utils(self) -> typing.Any:
        return utils

    @property
    def full_name(self) -> str:
        return display_name(self.me)

    @property
    def uid(self) -> int:
        return self.me.id

    @property
    def is_bot(self) -> bool:
        return bool(self.me.bot)

    @property
    def uptime(self) -> str:
        return time_formatter((time.time() - StartTime) * 1000)

    def to_dict(self) -> dict:
        return dict(inspect.getmembers(self))

    async def get_id(self, entity: hints.EntityLike) -> int:
        with suppress(ValueError):
            entity = int(entity)
        return await self.get_peer_id(entity)

    async def get_chat_id(self, *args, **kwargs) -> typing.Optional[int]:
        return await get_chat_id(*args, **kwargs)

    async def get_text(self, *args, **kwargs) -> str:
        return await get_text(*args, **kwargs)

    async def get_user(self, *args, **kwargs) -> typing.Optional[typing.Tuple[typ.User, str]]:
        return await get_user(*args, **kwargs)

    async def read(self, *args, **kwargs) -> bool:
        with suppress(BaseException):
            return await self.send_read_acknowledge(*args, **kwargs)
        return False

    async def block(self, entity: hints.EntityLike) -> bool:
        with suppress(BaseException):
            entity = await self.get_input_entity(entity)
            return await self(fun.contacts.BlockRequest(entity))
        return False

    async def unblock(self, entity: hints.EntityLike) -> bool:
        with suppress(BaseException):
            entity = await self.get_input_entity(entity)
            return await self(fun.contacts.UnblockRequest(entity))
        return False

    async def archive(self, entity: hints.EntityLike) -> typing.Optional[typ.Updates]:
        with suppress(BaseException):
            return await self.edit_folder(entity, folder=1)
        return None

    async def unarchive(self, entity: hints.EntityLike) -> typing.Optional[typ.Updates]:
        with suppress(BaseException):
            return await self.edit_folder(entity, folder=0)
        return None

    async def delete_chat(
        self,
        entity: hints.EntityLike,
        revoke: bool = False,
    ) -> typing.Optional[typ.Updates]:
        with suppress(BaseException):
            return await self.delete_dialog(entity, revoke=revoke)
        return None

    async def report_spam(self, entity: hints.EntityLike) -> bool:
        with suppress(BaseException):
            entity = await self.get_input_entity(entity)
            return await self(fun.messages.ReportSpamRequest(entity))
        return False

    async def send_reaction(
        self,
        entity: hints.EntityLike,
        message: hints.MessageIDLike,
        big: bool = False,
        add_to_recent: bool = False,
        reaction: typing.Optional[str] = None,
    ) -> typing.Optional[typ.Updates]:
        with suppress(BaseException):
            message = self.utils.get_message_id(message) or 0
            entity = await self.get_input_entity(entity)
            return await self(
                fun.messages.SendReactionRequest(
                    big=big,
                    add_to_recent=add_to_recent,
                    peer=entity,
                    msg_id=message,
                    reaction=[typ.ReactionEmoji(emoticon=reaction)],
                )
            )
        return None

    async def join_to(self, entity: hints.EntityLike) -> typing.Optional[typ.Updates]:
        with suppress(BaseException):
            entity = await self.get_input_entity(entity)
            return await self(fun.channels.JoinChannelRequest(entity))
        return None

    async def mute_chat(self, entity: hints.EntityLike) -> bool:
        with suppress(BaseException):
            entity = await self.get_input_entity(entity)
            return await self(
                fun.account.UpdateNotifySettingsRequest(
                    entity,
                    settings=typ.InputPeerNotifySettings(
                        show_previews=False,
                        silent=True,
                        mute_until=2**31 - 1,
                        sound=None,
                    ),
                )
            )
        return False

    async def create_group(
        self,
        title: str = "Getter",
        about: str = "",
        users: typing.Optional[typing.List[typing.Union[str, int]]] = None,
        photo: typing.Optional[str] = None,
    ) -> typing.Tuple[typing.Optional[str], typing.Optional[int]]:
        users = users or []
        try:
            created = await self(
                fun.channels.CreateChannelRequest(
                    title=title,
                    about=about,
                    megagroup=True,
                )
            )
            chat_id = created.chats[0].id
            await asyncio.sleep(6)
            link = await self(fun.messages.ExportChatInviteRequest(chat_id))
            if users:
                await asyncio.sleep(6)
                await self(
                    fun.channels.InviteToChannelRequest(
                        chat_id,
                        users=users,
                    )
                )
            if photo:
                await asyncio.sleep(6)
                await self(
                    fun.channels.EditPhotoRequest(
                        chat_id,
                        photo=typ.InputChatUploadedPhoto(photo),
                    ),
                )
        except Exception as err:
            self.logger.critical(err)
            return None, None
        if not str(chat_id).startswith("-100"):
            chat_id = int("-100" + str(chat_id))
        return link, chat_id


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
    session,
    app_version=__version__,
    device_model="Getter",
)
