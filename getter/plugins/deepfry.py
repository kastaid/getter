# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import mimetypes
import random
from PIL import Image, ImageEnhance, ImageOps
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl import types as typ
from . import (
    Root,
    kasta_cmd,
    plugins_help,
    events,
    suppress,
    aioify,
    Runner,
    Screenshot,
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
        await kst.eor("`I can't fry that!`", time=5)
        return
    if reply.sender.bot:
        await kst.eor("`Reply to actual users message.`", time=5)
        return
    yy = await kst.eor("`Frying...`")
    ext = None
    fry_img = Root / "downloads/fry.jpeg"
    if isinstance(reply.media, typ.MessageMediaPhoto):
        file = fry_img
    else:
        mim = reply.media.document.mime_type
        ext = mimetypes.guess_extension(mim)
        file = Root / ("downloads/" + f"fry{ext}")
    await reply.download_media(file=file)
    if ext and ext in (".mp4", ".gif", ".webm"):
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
    with suppress(BaseException):
        await kst.respond(
            file=resp.message.media,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await yy.try_delete()
    (file).unlink(missing_ok=True)
    (fry_img).unlink(missing_ok=True)


@kasta_cmd(
    pattern="deepfry(?: |$)([1-9])?",
    func=lambda e: e.is_reply,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    level = int(match) if match else 3
    reply = await kst.get_reply_message()
    data = check_media(reply)
    if isinstance(data, bool):
        await kst.eor("`I can't deepfry that!`", time=5)
        return
    if reply.sender.bot:
        await kst.eor("`Reply to actual users message.`", time=5)
        return
    yy = await kst.eor("`Deepfrying...`")
    ext = None
    fry_img = Root / "downloads/fry.jpeg"
    if isinstance(reply.media, typ.MessageMediaPhoto):
        file = fry_img
    else:
        mim = reply.media.document.mime_type
        ext = mimetypes.guess_extension(mim)
        file = Root / ("downloads/" + f"fry{ext}")
    await reply.download_media(file=file)
    if ext and ext in (".mp4", ".gif", ".webm"):
        to_deepfry = fry_img
        ss = await Screenshot(file, 0, fry_img)
        if not ss:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    else:
        if ext and ext == ".tgs":
            fry_img = Root / "downloads/fry.png"
            await Runner(f"lottie_convert.py {file} {fry_img}")
            (file).unlink(missing_ok=True)
            file = fry_img
        to_deepfry = file
    try:
        for _ in range(level):
            img = await aioify(deepfry, to_deepfry)
        img.save(fry_img, format="JPEG")
    except BaseException:
        (to_deepfry).unlink(missing_ok=True)
        return await yy.try_delete()
    with suppress(BaseException):
        await kst.respond(
            file=fry_img,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await yy.try_delete()
    (file).unlink(missing_ok=True)
    (fry_img).unlink(missing_ok=True)


async def conv_fry(conv, image, level):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        media = await conv.send_file(
            image,
            force_document=False,
            allow_cache=False,
        )
        resp = await resp
        await resp.try_delete()
        yy = await conv.send_message(f"/deepfry {level}", reply_to=media.id)
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        resp = await resp
        await yy.try_delete()
        await resp.mark_read(clear_mentions=True)
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_fry(conv, image, level)


def deepfry(img: Image) -> Image:
    img = Image.open(img)
    colours = (
        (random.randint(50, 200), random.randint(40, 170), random.randint(40, 190)),
        (random.randint(190, 255), random.randint(170, 240), random.randint(180, 250)),
    )
    img = img.copy().convert("RGB")
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize(
        (int(width ** random.uniform(0.8, 0.9)), int(height ** random.uniform(0.8, 0.9))),
        resample=Image.LANCZOS,
    )
    img = img.resize(
        (int(width ** random.uniform(0.85, 0.95)), int(height ** random.uniform(0.85, 0.95))),
        resample=Image.BILINEAR,
    )
    img = img.resize(
        (int(width ** random.uniform(0.89, 0.98)), int(height ** random.uniform(0.89, 0.98))),
        resample=Image.BICUBIC,
    )
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, random.randint(3, 7))
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(random.uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(random.uniform(1.0, 2.0))
    overlay = ImageOps.colorize(overlay, colours[0], colours[1])
    img = Image.blend(img, overlay, random.uniform(0.1, 0.4))
    return ImageEnhance.Sharpness(img).enhance(random.randint(5, 300))


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
    "{i}deepfry [1-9] [reply]": "Deepfy any image/sticker/animation/gif/video and make it look ugly (default level 1).",
}
