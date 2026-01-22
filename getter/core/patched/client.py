# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import random

import telethon.client.telegramclient
from telethon import hints, utils
from telethon.tl import functions as fun, types as typ

from getter.core.constants import MAX_MESSAGE_LEN
from getter.core.functions import get_chat_id, get_text, get_user
from getter.core.patcher import patch, patchable

delattr(fun.account, "DeleteAccountRequest")


@patch(telethon.client.telegramclient.TelegramClient)
class TelegramClient:
    @patchable()
    async def get_id(self, entity: hints.EntityLike) -> int:
        try:
            entity = int(entity)
        except ValueError:
            pass
        return await self.get_peer_id(entity)

    @patchable()
    async def get_chat_id(self, *args, **kwargs) -> int | None:
        return await get_chat_id(*args, **kwargs)

    @patchable()
    async def get_text(self, *args, **kwargs) -> str:
        return await get_text(*args, **kwargs)

    @patchable()
    async def get_user(self, *args, **kwargs) -> tuple[typ.User, str] | None:
        return await get_user(*args, **kwargs)

    @patchable()
    async def read_chat(self, *args, **kwargs) -> bool:
        try:
            return await self.send_read_acknowledge(*args, **kwargs)
        except BaseException:
            return False

    @patchable()
    async def block(self, entity: hints.EntityLike) -> bool:
        try:
            entity = await self.get_input_entity(entity)
            return await self(fun.contacts.BlockRequest(entity))
        except BaseException:
            return False

    @patchable()
    async def unblock(self, entity: hints.EntityLike) -> bool:
        try:
            entity = await self.get_input_entity(entity)
            return await self(fun.contacts.UnblockRequest(entity))
        except BaseException:
            return False

    @patchable()
    async def archive(self, entity: hints.EntityLike) -> typ.Updates | None:
        try:
            return await self.edit_folder(entity, folder=1)
        except BaseException:
            return None

    @patchable()
    async def unarchive(self, entity: hints.EntityLike) -> typ.Updates | None:
        try:
            return await self.edit_folder(entity, folder=0)
        except BaseException:
            return None

    @patchable()
    async def delete_chat(
        self,
        entity: hints.EntityLike,
        revoke: bool = False,
    ) -> typ.Updates | None:
        try:
            return await self.delete_dialog(entity, revoke=revoke)
        except BaseException:
            return None

    @patchable()
    async def report_spam(self, entity: hints.EntityLike) -> bool:
        try:
            entity = await self.get_input_entity(entity)
            return await self(fun.messages.ReportSpamRequest(entity))
        except BaseException:
            return False

    @patchable()
    async def send_reaction(
        self,
        entity: hints.EntityLike,
        message: hints.MessageIDLike,
        big: bool = False,
        add_to_recent: bool = False,
        reaction: str | None = None,
    ) -> typ.Updates | None:
        try:
            message = utils.get_message_id(message) or 0
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
        except BaseException:
            return None

    @patchable()
    async def join_to(self, entity: hints.EntityLike) -> typ.Updates | None:
        try:
            entity = await self.get_input_entity(entity)
            return await self(fun.channels.JoinChannelRequest(entity))
        except BaseException:
            return None

    @patchable()
    async def mute_chat(self, entity: hints.EntityLike) -> bool:
        try:
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
        except BaseException:
            return False

    @patchable()
    async def create_group(
        self,
        title: str = "Getter",
        about: str = "",
        users: list[str | int] | None = None,
        photo: str | None = None,
    ) -> tuple[str | None, int | None]:
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
            self.log.critical(err)
            return None, None
        if not str(chat_id).startswith("-100"):
            chat_id = int("-100" + str(chat_id))
        return link, chat_id

    @patchable()
    async def send_message_parts(
        self,
        entity: hints.EntityLike,
        text: str,
        **kwargs,
    ) -> typ.Message:
        if len(text) > MAX_MESSAGE_LEN:
            parts = []
            while len(text):
                splits = text[:MAX_MESSAGE_LEN].rfind("\n")
                if splits != -1:
                    parts.append(text[:splits])
                    text = text[splits + 1 :]
                else:
                    splits = text[:MAX_MESSAGE_LEN].rfind(". ")
                    if splits != -1:
                        parts.append(text[: splits + 1])
                        text = text[splits + 2 :]
                    else:
                        parts.append(text[:MAX_MESSAGE_LEN])
                        text = text[MAX_MESSAGE_LEN:]
            msg = None
            for part in parts[:-1]:
                msg = await self.send_message(entity, part, **kwargs)
                await asyncio.sleep(random.uniform(1, 3))
            return msg
        return await self.send_message(entity, text, **kwargs)
