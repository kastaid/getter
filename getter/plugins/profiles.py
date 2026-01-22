# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio

from telethon.tl import functions as fun, types as typ

from . import (
    Root,
    formatx_send,
    get_media_type,
    kasta_cmd,
    plugins_help,
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
        await yy.eor(formatx_send(err), parse_mode="html")


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
        await yy.eor(formatx_send(err), parse_mode="html")


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
        await yy.eor(formatx_send(err), parse_mode="html")


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
        (Root / pull).unlink(missing_ok=True)
        await yy.eod("`Successfully change my profile picture.`")
    except Exception as err:
        (Root / pull).unlink(missing_ok=True)
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="delpp(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    args = await ga.get_text(kst)
    yy = await kst.eor("`Processing...`")
    if any(_ in args.lower() for _ in ("-a", "all")):
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
        await yy.eor(formatx_send(err), parse_mode="html")


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
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="getpp(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    user, args = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    is_all = any(_ in args.lower() for _ in ("-a", "all"))
    total = (await ga.get_profile_photos(user.id, limit=0)).total or 0
    if not total:
        return await yy.eor("`User doesn't have profile picture!`", time=3)
    try:
        async for photo in ga.iter_profile_photos(user.id):
            await yy.eor(
                file=photo,
                force_document=False,
            )
            if not is_all:
                break
            await asyncio.sleep(1)
        total = total if is_all else 1
        await yy.sod(f"`Successfully to get {total} profile picture(s).`", time=8)
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


plugins_help["profiles"] = {
    "{i}pbio [bio]": "Change my profile bio. If empty the current bio removed.",
    "{i}pname [first_name] ; [last_name]": "Change my profile name. If empty the current name set to blank `ㅤ`.",
    "{i}puname [username]": "Change my profile username. If empty the current username removed.",
    "{i}ppic [reply_media]": "Change my profile picture.",
    "{i}delpp [number]/[-a/all]": "Delete my profile picture by given number or delete one if empty or add '-a' to delete all profile pictures.",
    "{i}hidepp": "Hidden my profile pictures for everyone (change privacy).",
    "{i}showpp": "Showing my profile pictures.",
    "{i}getpp [reply]/[username/mention/id] [-a/all]": "Get profile pictures of user. Add '-a' to get all pictures.",
}
