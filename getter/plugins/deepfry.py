# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from mimetypes import guess_extension
from random import randint, uniform

from PIL import Image, ImageEnhance, ImageOps
from telethon import events
from telethon.errors import YouBlockedUserError
from telethon.tl import types as typ

from . import (
    Root,
    Runner,
    Screenshot,
    aioify,
    kasta_cmd,
    plugins_help,
)

FRY_BOT = "image_deepfrybot"


@kasta_cmd(
    pattern="fry(?: |$)([1-8])?",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    match = kst.pattern_match.group(1)
    level = int(match) if match else 3
    reply = await kst.get_reply_message()
    data = check_media(reply)
    if isinstance(data, bool):
        return await kst.eor("`Cannot frying that!`", time=5)
    yy = await kst.eor("`...`")
    ext = None
    fry_img = Root / "downloads/fry.jpeg"
    if isinstance(reply.media, typ.MessageMediaPhoto):
        file = fry_img
    else:
        mim = reply.media.document.mime_type
        ext = guess_extension(mim)
        file = Root / ("downloads/" + f"fry{ext}")
    await reply.download_media(file=file)
    if ext and ext in {".mp4", ".gif", ".webm"}:
        ss = await Screenshot(file, 0, fry_img)
        if not ss:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    else:
        try:
            if ext and ext == ".tgs":
                fry_img = Root / "downloads/fry.png"
                await Runner(f"lottie_convert.py {file} {fry_img}")
                (file).unlink(missing_ok=True)
                file = fry_img
            img = Image.open(file)
            img.convert("RGB").save(fry_img, format="JPEG")
        except BaseException:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    async with ga.conversation(FRY_BOT) as conv:
        resp = await conv_fry(conv, fry_img, level)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "photo", None):
        return await yy.eod(f"`{resp.message.message}`")
    await yy.eor(
        file=resp.message.media,
        force_document=False,
    )
    (file).unlink(missing_ok=True)
    (fry_img).unlink(missing_ok=True)


@kasta_cmd(
    pattern="ugly(?: |$)([1-9])?",
    func=lambda e: e.is_reply,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    level = int(match) if match else 3
    reply = await kst.get_reply_message()
    data = check_media(reply)
    if isinstance(data, bool):
        return await kst.eor("`Cannot uglying that!`", time=5)
    yy = await kst.eor("`...`")
    ext = None
    ugly_img = Root / "downloads/ugly.jpeg"
    if isinstance(reply.media, typ.MessageMediaPhoto):
        file = ugly_img
    else:
        mim = reply.media.document.mime_type
        ext = guess_extension(mim)
        file = Root / ("downloads/" + f"ugly{ext}")
    await reply.download_media(file=file)
    if ext and ext in {".mp4", ".gif", ".webm"}:
        to_ugly = ugly_img
        ss = await Screenshot(file, 0, ugly_img)
        if not ss:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    else:
        if ext and ext == ".tgs":
            ugly_img = Root / "downloads/ugly.png"
            await Runner(f"lottie_convert.py {file} {ugly_img}")
            (file).unlink(missing_ok=True)
            file = ugly_img
        to_ugly = file
    try:
        for _ in range(level):
            img = await aioify(uglying, to_ugly)
        img.save(ugly_img, format="JPEG")
    except BaseException:
        (to_ugly).unlink(missing_ok=True)
        return await yy.try_delete()
    await yy.eor(
        file=ugly_img,
        force_document=False,
    )
    (file).unlink(missing_ok=True)
    (ugly_img).unlink(missing_ok=True)


async def conv_fry(conv, image, level):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        media = await conv.send_file(
            image,
            force_document=False,
        )
        resp = await resp
        await resp.try_delete()
        yy = await conv.send_message(f"/deepfry {level}", reply_to=media.id)
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        resp = await resp
        await yy.try_delete()
        await resp.read(
            clear_mentions=True,
            clear_reactions=True,
        )
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_fry(conv, image, level)


def uglying(img: Image) -> Image:
    img = Image.open(img)
    colours = (
        (randint(50, 200), randint(40, 170), randint(40, 190)),
        (randint(190, 255), randint(170, 240), randint(180, 250)),
    )
    img = img.copy().convert("RGB")
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize(
        (int(width ** uniform(0.8, 0.9)), int(height ** uniform(0.8, 0.9))),
        resample=Image.LANCZOS,
    )
    img = img.resize(
        (int(width ** uniform(0.85, 0.95)), int(height ** uniform(0.85, 0.95))),
        resample=Image.BILINEAR,
    )
    img = img.resize(
        (int(width ** uniform(0.89, 0.98)), int(height ** uniform(0.89, 0.98))),
        resample=Image.BICUBIC,
    )
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, randint(3, 7))
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageOps.colorize(overlay, colours[0], colours[1])
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    return ImageEnhance.Sharpness(img).enhance(randint(5, 300))


def check_media(reply):
    data = False
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if reply.audio or reply.voice:
                return False
            data = reply.media.document
        else:
            return False
    if not data or data is None:
        return False
    return data


plugins_help["deepfry"] = {
    "{i}fry [1-8] [reply]": "Frying any image/sticker/animation/gif/video use image_deepfrybot (default level 3).",
    "{i}ugly [1-9] [reply]": "Uglying any image/sticker/animation/gif/video and make it look ugly (default level 1).",
}
