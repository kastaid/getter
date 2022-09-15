# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from . import (
    kasta_cmd,
    plugins_help,
    choice,
    time_formatter,
)


@kasta_cmd(
    pattern="f(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
    no_crash=True,
)
@kasta_cmd(
    pattern="gf(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
    dev=True,
    no_crash=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    action = kst.pattern_match.group(1)
    act = action
    if action in ("audio", "round", "video"):
        action = "record-" + action
    sec = await ga.get_text(kst, group=2)
    sec = int(60 if not sec.replace(".", "", 1).isdecimal() else sec)
    typefor = time_formatter(sec * 1000)
    await kst.eor(f"`Starting fake {act} for {typefor}...`", time=3)
    async with ga.action(kst.chat_id, action=action):
        await asyncio.sleep(sec)


plugins_help["fakeaction"] = {
    "{i}ftyping [seconds]/[reply]": "Show Fake Typing action in current chat.",
    "{i}faudio [seconds]/[reply]": "Show Fake Recording action in current chat.",
    "{i}fvideo [seconds]/[reply]": "Show Fake Video action in current chat.",
    "{i}fgame [seconds]/[reply]": "Show Fake Game Playing action in current chat.",
    "{i}fsticker [seconds]/[reply]": "Show Fake Sticker Choosing action in current chat.",
    "{i}flocation [seconds]/[reply]": "Show Fake Location action in current chat.",
    "{i}fcontact [seconds]/[reply]": "Show Fake Contact Choosing action in current chat.",
    "{i}fround [seconds]/[reply]": "Show Fake Video Message action in current chat.",
    "{i}fphoto [seconds]/[reply]": "Show Fake Sending Photo action in current chat.",
    "{i}fdocument [seconds]/[reply]": "Show Fake Sending Document action in current chat.",
}
