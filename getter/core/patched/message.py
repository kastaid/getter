# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import typing
from contextlib import suppress
from io import BytesIO
from telethon import hints
from telethon.client.chats import _ChatAction
from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError,
    MessageNotModifiedError,
    MediaCaptionTooLongError,
    MessageTooLongError,
    ChatSendMediaForbiddenError,
    FloodWaitError,
)
from telethon.tl import types as typ, custom
from ..patcher import patch, patchable


@patch(custom.message.Message)
class Message(typ.Message):
    @patchable()
    async def eor(
        self,
        text: typing.Optional[str] = None,
        link_preview: bool = False,
        silent: bool = False,
        time: typing.Optional[typing.Union[int, float]] = None,
        edit_time: typing.Optional[typing.Union[int, float]] = None,
        force_reply: bool = False,
        parts: bool = False,
        **args,
    ) -> typing.Optional[typing.Union[typ.Message, typing.Sequence[typ.messages.AffectedMessages]]]:
        if self is None:
            return
        _ = args.get("reply_to", None)
        reply_to = _ if _ else (self.reply_to_msg_id or (self if force_reply else None))
        is_file = "file" in args and args.get("file", "") and not self.media
        for arg in (
            "entity",
            "message",
            "text",
            "link_preview",
            "silent",
            "reply_to",
        ):
            if arg in args:
                del args[arg]
        if self.out and not isinstance(self, typ.MessageService):
            if edit_time:
                await asyncio.sleep(edit_time)
            if is_file or parts:
                await self.delete()
            try:
                if is_file:
                    yy = await self._client.send_file(
                        self.chat_id,
                        caption=text,
                        silent=True,
                        reply_to=reply_to,
                        **args,
                    )
                else:
                    if parts:
                        yy = await self._client.send_message_parts(
                            self.chat_id,
                            text,
                            link_preview=link_preview,
                            silent=silent,
                            reply_to=reply_to,
                            **args,
                        )
                    else:
                        yy = await self.edit(
                            text,
                            link_preview=link_preview,
                            **args,
                        )
            except MessageIdInvalidError:  # keep functions running
                return None
            except MessageNotModifiedError:
                yy = self
            except MediaCaptionTooLongError:
                try:
                    yy = await self._client.send_file(
                        self.chat_id,
                        caption=None,
                        silent=True,
                        reply_to=reply_to,
                        **args,
                    )
                except BaseException:
                    return None
            except MessageTooLongError:
                await self.delete()
                with suppress(BaseException), BytesIO(str.encode(text)) as file:
                    file.name = "message.txt"
                    return await self.respond(
                        r"\\<b>#Getter</b>// Message Too Long",
                        file=file,
                        force_document=True,
                        silent=True,
                        reply_to=reply_to,
                        parse_mode="html",
                    )
                return None
            except (ChatSendMediaForbiddenError, FloodWaitError):
                raise
            except BaseException:
                return None
        else:
            try:
                if is_file:
                    yy = await self._client.send_file(
                        self.chat_id,
                        caption=text,
                        silent=True,
                        reply_to=reply_to,
                        **args,
                    )
                else:
                    if parts:
                        yy = await self._client.send_message_parts(
                            self.chat_id,
                            text,
                            link_preview=link_preview,
                            silent=silent,
                            reply_to=reply_to,
                            **args,
                        )
                    else:
                        yy = await self.respond(
                            text,
                            link_preview=link_preview,
                            silent=silent,
                            reply_to=reply_to,
                            **args,
                        )
            except MediaCaptionTooLongError:
                try:
                    yy = await self._client.send_file(
                        self.chat_id,
                        caption=None,
                        silent=True,
                        reply_to=reply_to,
                        **args,
                    )
                except BaseException:
                    return None
            except MessageTooLongError:
                with suppress(BaseException), BytesIO(str.encode(text)) as file:
                    file.name = "message.txt"
                    return await self.respond(
                        r"\\<b>#Getter</b>// Message Too Long",
                        file=file,
                        force_document=True,
                        silent=True,
                        reply_to=reply_to,
                        parse_mode="html",
                    )
                return None
            except (ChatSendMediaForbiddenError, FloodWaitError):
                raise
            except BaseException:
                return None
        if yy and time:
            await asyncio.sleep(time)
            return await yy.delete()
        return yy

    @patchable()
    async def eod(
        self, *args, **kwargs
    ) -> typing.Optional[typing.Union[typ.Message, typing.Sequence[typ.messages.AffectedMessages]]]:
        kwargs["time"] = kwargs.get("time", 8)
        return await self.eor(*args, **kwargs)

    @patchable()
    async def sod(
        self,
        text: typing.Optional[str] = None,
        chat_id: typing.Optional[hints.EntityLike] = None,
        link_preview: bool = False,
        silent: bool = False,
        time: typing.Optional[typing.Union[int, float]] = None,
        edit_time: typing.Optional[typing.Union[int, float]] = None,
        force_reply: bool = False,
        delete: bool = True,
        parts: bool = False,
        **args,
    ) -> typing.Optional[typing.Union[typ.Message, typing.Sequence[typ.messages.AffectedMessages]]]:
        if self is None:
            return
        chat_id = chat_id or self.chat_id
        _ = args.get("reply_to", None)
        reply_to = _ if _ else (self.reply_to_msg_id or (self if force_reply else None))
        is_file = "file" in args and args.get("file", "") and not self.media
        for arg in (
            "entity",
            "message",
            "link_preview",
            "silent",
            "reply_to",
        ):
            if arg in args:
                del args[arg]
        if self.out and delete:
            await self.delete()
        try:
            if is_file:
                yy = await self._client.send_file(
                    chat_id,
                    caption=text,
                    silent=True,
                    reply_to=reply_to,
                    **args,
                )
            else:
                if parts:
                    yy = await self._client.send_message_parts(
                        chat_id,
                        text,
                        link_preview=link_preview,
                        silent=silent,
                        reply_to=reply_to,
                        **args,
                    )
                else:
                    yy = await self._client.send_message(
                        chat_id,
                        text,
                        link_preview=link_preview,
                        silent=silent,
                        reply_to=reply_to,
                        **args,
                    )
        except MediaCaptionTooLongError:
            try:
                yy = await self._client.send_file(
                    chat_id,
                    caption=None,
                    silent=True,
                    reply_to=reply_to,
                    **args,
                )
            except BaseException:
                return None
        except MessageTooLongError:
            if self.out:
                await self.delete()
            with suppress(BaseException), BytesIO(str.encode(text)) as file:
                file.name = "message.txt"
                return await self.respond(
                    r"\\<b>#Getter</b>// Message Too Long",
                    file=file,
                    force_document=True,
                    silent=True,
                    reply_to=reply_to,
                    parse_mode="html",
                )
            return None
        except (ChatSendMediaForbiddenError, FloodWaitError):
            raise
        except BaseException:
            return None
        if yy and time:
            await asyncio.sleep(time)
            return await yy.delete()
        return yy

    @patchable()
    async def try_delete(self) -> typing.Optional[typing.Sequence[typ.messages.AffectedMessages]]:
        try:
            return await self.delete()
        except BaseException:
            return None

    @patchable()
    async def read(self, *args, **kwargs) -> bool:
        return await self._client.read_chat(
            await self.get_input_chat(),
            max_id=self.id,
            *args,
            **kwargs,
        )

    @patchable()
    async def send_react(self, *args, **kwargs) -> typing.Optional[typ.Updates]:
        kwargs["message"] = self.id
        return await self._client.send_reaction(await self.get_input_chat(), *args, **kwargs)

    @patchable()
    async def send_action(self, *args, **kwargs) -> typing.Union[_ChatAction, typing.Coroutine]:
        return self._client.action(await self.get_input_chat(), *args, **kwargs)

    @patchable(prop=True)
    def msg_link(self) -> typing.Optional[str]:
        if hasattr(self.chat, "username") and self.chat.username:
            return f"https://t.me/{self.chat.username}/{self.id}"
        if self.chat and self.chat.id:
            chat = self.chat.id
        elif self.chat_id:
            if str(self.chat_id).startswith(("-100", "-")):
                chat = int(str(self.chat_id).replace("-100", "").replace("-", ""))
            else:
                chat = self.chat_id
        else:
            return None
        if self.is_private:
            return f"tg://openmessage?user_id={chat}&message_id={self.id}"
        return f"https://t.me/c/{chat}/{self.id}"
