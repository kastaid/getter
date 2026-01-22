# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from collections.abc import Coroutine, Sequence
from contextlib import suppress
from io import BytesIO

import telethon.tl.custom
from telethon import hints
from telethon.client.chats import _ChatAction
from telethon.errors import (
    ChatSendMediaForbiddenError,
    FloodWaitError,
    MediaCaptionTooLongError,
    MessageIdInvalidError,
    MessageNotModifiedError,
    MessageTooLongError,
)
from telethon.tl import types as typ

from getter.core.patcher import patch, patchable


@patch(telethon.tl.custom.message.Message)
class Message:
    @patchable()
    async def eor(
        self,
        text: str | None = None,
        link_preview: bool = False,
        silent: bool = False,
        time: int | float | None = None,
        edit_time: int | float | None = None,
        force_reply: bool = False,
        parts: bool = False,
        **args,
    ) -> typ.Message | Sequence[typ.messages.AffectedMessages] | None:
        if self is None:
            return
        _ = args.get("reply_to")
        reply_to = _ or (self.reply_to_msg_id or (self if force_reply else None))
        is_file = "file" in args and args.get("file", "") and not self.media
        for arg in (
            "entity",
            "message",
            "text",
            "link_preview",
            "silent",
            "reply_to",
        ):
            args.pop(arg, None)
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
    async def eod(self, *args, **kwargs) -> typ.Message | Sequence[typ.messages.AffectedMessages] | None:
        kwargs["time"] = kwargs.get("time", 8)
        return await self.eor(*args, **kwargs)

    @patchable()
    async def sod(
        self,
        text: str | None = None,
        chat_id: hints.EntityLike | None = None,
        link_preview: bool = False,
        silent: bool = False,
        time: int | float | None = None,
        edit_time: int | float | None = None,
        force_reply: bool = False,
        delete: bool = True,
        parts: bool = False,
        **args,
    ) -> typ.Message | Sequence[typ.messages.AffectedMessages] | None:
        if self is None:
            return
        chat_id = chat_id or self.chat_id
        _ = args.get("reply_to")
        reply_to = _ or (self.reply_to_msg_id or (self if force_reply else None))
        is_file = "file" in args and args.get("file", "") and not self.media
        for arg in (
            "entity",
            "message",
            "link_preview",
            "silent",
            "reply_to",
        ):
            args.pop(arg, None)
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
    async def try_delete(self) -> Sequence[typ.messages.AffectedMessages] | None:
        try:
            return await self.delete()
        except BaseException:
            return None

    @patchable()
    async def read(self, **args) -> bool:
        return await self._client.read_chat(
            entity=await self.get_input_chat(),
            max_id=self.id,
            **args,
        )

    @patchable()
    async def send_react(self, **args) -> typ.Updates | None:
        args["message"] = self.id
        return await self._client.send_reaction(
            entity=await self.get_input_chat(),
            **args,
        )

    @patchable()
    async def send_action(self, **args) -> _ChatAction | Coroutine:
        return self._client.action(
            entity=await self.get_input_chat(),
            **args,
        )

    @patchable(True)
    def msg_link(self) -> str | None:
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
