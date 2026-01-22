# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from random import choice

from . import kasta_cmd, plugins_help, time_formatter


@kasta_cmd(
    pattern="f(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
)
@kasta_cmd(
    pattern="gf(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    action = kst.pattern_match.group(1)
    act = action
    if action in {"audio", "round", "video"}:
        action = "record-" + action
    sec = await kst.client.get_text(kst, group=2)
    sec = int(60 if not sec.replace(".", "", 1).isdecimal() else sec)
    typefor = time_formatter(sec * 1000)
    await kst.eor(f"`Starting fake {act} for {typefor}...`", time=3, silent=True)
    async with await kst.send_action(action=action):
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
