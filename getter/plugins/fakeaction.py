# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
from . import HELP, DEVS, kasta_cmd


@kasta_cmd(
    pattern="f(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
    no_crash=True,
)
@kasta_cmd(
    pattern="gf(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
    own=True,
    senders=DEVS,
    no_crash=True,
)
async def _(kst):
    action = kst.pattern_match.group(1)
    if action in ("audio", "round", "video"):
        action = "record-" + action
    sec = kst.pattern_match.group(2)
    sec = 60 if not sec.replace(".", "", 1).isdecimal() else sec
    act = kst.pattern_match.group(1).capitalize()
    await kst.eor(f'Starting "Fake {act}" for `{sec}` seconds.', time=3)
    async with kst.client.action(kst.chat_id, action):
        await asyncio.sleep(int(sec))


HELP.update(
    {
        "fakeaction": [
            "Fake Action",
            """❯ `{i}ftyping <time/in seconds>`
Show Fake Typing action in current chat.

❯ `{i}faudio <time/in seconds>`
Show Fake Recording action in current chat.

❯ `{i}fvideo <time/in seconds>`
Show Fake Video action in current chat.

❯ `{i}fgame <time/in seconds>`
Show Fake Game Playing action in current chat.

❯ `{i}fsticker <time/in seconds>`
Show Fake Sticker Choosing action in current chat.

❯ `{i}flocation <time/in seconds>`
Show Fake Location action in current chat.

❯ `{i}fcontact <time/in seconds>`
Show Fake Contact Choosing action in current chat.

❯ `{i}fround <time/in seconds>`
Show Fake Video Message action in current chat.

❯ `{i}fphoto <time/in seconds>`
Show Fake Sending Photo action in current chat.

❯ `{i}fdocument <time/in seconds>`
Show Fake Sending Document action in current chat.
""",
        ]
    }
)
