# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import telethon.tl.custom.conversation
from telethon.tl.custom.conversation import _checks_cancelled

from getter.core.patcher import patch, patchable


@patch(telethon.tl.custom.conversation.Conversation)
class Conversation:
    @patchable()
    @_checks_cancelled
    async def read(
        self,
        message: int | None = None,
        **args,
    ):
        if message is None:
            message = self._incoming[-1].id if self._incoming else 0
        elif not isinstance(message, int):
            message = message.id
        return await self._client.read_chat(
            entity=self._input_chat,
            max_id=message,
            **args,
        )
