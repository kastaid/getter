# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import random

from . import format_time, kasta_cmd, plugins_help


@kasta_cmd(
    pattern="f(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
)
@kasta_cmd(
    pattern="gf(typing|audio|contact|document|game|location|sticker|photo|round|video)(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(random.choice((4, 6, 8)))
    action = kst.pattern_match.group(1)
    act = action
    if action in {"audio", "round", "video"}:
        action = "record-" + action
    sec = await kst.client.get_text(kst, group=2)
    sec = int(60 if not sec.replace(".", "", 1).isdecimal() else sec)
    typefor = format_time(sec)
    await kst.eor(f"`Starting fake {act} for {typefor}...`", time=3, silent=True)
    async with await kst.send_action(action=action):
        await asyncio.sleep(sec)


plugins_help["fakeaction"] = {
    "{pfx}ftyping [seconds]/[reply]": "Show Fake Typing action in current chat.",
    "{pfx}faudio [seconds]/[reply]": "Show Fake Recording action in current chat.",
    "{pfx}fvideo [seconds]/[reply]": "Show Fake Video action in current chat.",
    "{pfx}fgame [seconds]/[reply]": "Show Fake Game Playing action in current chat.",
    "{pfx}fsticker [seconds]/[reply]": "Show Fake Sticker Choosing action in current chat.",
    "{pfx}flocation [seconds]/[reply]": "Show Fake Location action in current chat.",
    "{pfx}fcontact [seconds]/[reply]": "Show Fake Contact Choosing action in current chat.",
    "{pfx}fround [seconds]/[reply]": "Show Fake Video Message action in current chat.",
    "{pfx}fphoto [seconds]/[reply]": "Show Fake Sending Photo action in current chat.",
    "{pfx}fdocument [seconds]/[reply]": "Show Fake Sending Document action in current chat.",
}
