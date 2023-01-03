# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import typing
from telethon.tl.custom.conversation import _checks_cancelled, Conversation as _Conversation
from ..patcher import patch, patchable


@patch(_Conversation)
class Conversation:
    @patchable()
    @_checks_cancelled
    async def read(
        self,
        message: typing.Optional[int] = None,
        **args,
    ):
        if message is None:
            message = self._incoming[-1].id if self._incoming else 0
        elif not isinstance(message, int):
            message = message.id
        return await self._client.read_chat(
            self._input_chat,
            max_id=message,
            **args,
        )
