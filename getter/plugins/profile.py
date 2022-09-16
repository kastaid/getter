# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from telethon.tl import functions as fun, types as typ
from . import (
    Root,
    kasta_cmd,
    plugins_help,
    get_media_type,
    parse_pre,
)


@kasta_cmd(
    pattern="pbio(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    about = await ga.get_text(kst)
    yy = await kst.eor("`Processing...`")
    try:
        await ga(fun.account.UpdateProfileRequest(about=about))
        await yy.eod(f"`Successfully change my bio to “{about}”.`")
    except Exception as err:
        await yy.eor(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern="pname(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    name = await ga.get_text(kst) or "ㅤ"
    yy = await kst.eor("`Processing...`")
    first_name, last_name = name, ""
    if ";" in name:
        first_name, last_name = name.split(";", 1)
    try:
        await asyncio.sleep(1)
        await ga(
            fun.account.UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name,
            ),
        )
        names = f"{first_name} {last_name}".strip()
        await yy.eod(f"`Successfully change my name to “{names}”.`")
    except Exception as err:
        await yy.eor(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern="puname(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    username = await ga.get_text(kst)
    yy = await kst.eor("`Processing...`")
    try:
        await asyncio.sleep(1)
        await ga(fun.account.UpdateUsernameRequest(username))
        await yy.eod(f"`Successfully change my username to “{username}”.`")
    except Exception as err:
        await yy.eor(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern="ppic$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    reply = await kst.get_reply_message()
    pull = await reply.download_media(file="downloads")
    file = await ga.upload_file(pull)
    try:
        if "pic" in get_media_type(reply.media):
            await ga(fun.photos.UploadProfilePhotoRequest(file))
        else:
            await ga(fun.photos.UploadProfilePhotoRequest(video=file))
        await yy.eod("`Successfully change my profile picture.`")
    except Exception as err:
        await yy.eor(str(err), parse_mode=parse_pre)
    (Root / pull).unlink(missing_ok=True)


@kasta_cmd(
    pattern="delpp(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    args = await ga.get_text(kst)
    yy = await kst.eor("`Processing...`")
    if "all" in args:
        limit = 0
    elif args.isdecimal():
        limit = int(args)
    else:
        limit = 1
    try:
        pplist = await ga.get_profile_photos("me", limit=limit)
        await ga(fun.photos.DeletePhotosRequest(pplist))
        await yy.eod(f"`Successfully deleted {len(pplist)} profile picture(s).`")
    except Exception as err:
        await yy.eor(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern="(show|hide)pp$",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    toggle = kst.pattern_match.group(1)
    rule = typ.InputPrivacyValueAllowAll() if toggle == "show" else typ.InputPrivacyValueDisallowAll()
    try:
        await asyncio.sleep(1)
        await ga(
            fun.account.SetPrivacyRequest(
                key=typ.InputPrivacyKeyProfilePhoto(),
                rules=[rule],
            )
        )
        await yy.eod(f"`Successfully {toggle} my profile picture.`")
    except Exception as err:
        await yy.eor(str(err), parse_mode=parse_pre)


plugins_help["profile"] = {
    "{i}pbio [bio]": "Change my profile bio. If empty the current bio removed.",
    "{i}pname [first_name] ; [last_name]": "Change my profile name. If empty the current name set to blank `ㅤ`.",
    "{i}puname [username]": "Change my profile username. If empty the current username removed.",
    "{i}ppic [reply_media]": "Change my profile picture.",
    "{i}delpp [number]/[all]": "Delete my profile picture by given number or delete one if empty or add 'all' to delete all profile pictures.",
    "{i}hidepp": "Hidden my profile pictures for everyone (change privacy).",
    "{i}showpp": "Showing my profile pictures.",
}
