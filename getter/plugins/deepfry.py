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
from telethon.events import NewMessage
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import MessageMediaPhoto, DocumentAttributeFilename
from . import (
    Root,
    kasta_cmd,
    plugins_help,
    suppress,
    make_async,
    Screenshot,
)

FRY_BOT = "image_deepfrybot"


@kasta_cmd(
    pattern="fry(?: |$)([1-8])?",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
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
    resp = None
    ext = None
    fry_image = Root / "downloads/fry.jpeg"
    if isinstance(reply.media, MessageMediaPhoto):
        file = fry_image
    else:
        mim = reply.media.document.mime_type
        ext = mimetypes.guess_extension(mim)
        file = Root / ("downloads/" + f"fry{ext}")
    await kst.client.download_media(reply.media, file=file)
    if ext and ext in (".mp4", ".gif", ".webm"):
        ss = await Screenshot(file, 0, fry_image)
        if not ss:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    else:
        try:
            img = Image.open(file)
            img.convert("RGB").save(fry_image, format="JPEG")
        except BaseException:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    async with kst.client.conversation(FRY_BOT) as conv:
        resp = await conv_fry(conv, fry_image, level)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "photo", None):
        return await yy.eod(f"`{resp.message.message}`")
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=resp.message.media,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await yy.try_delete()
    (file).unlink(missing_ok=True)
    (fry_image).unlink(missing_ok=True)


@kasta_cmd(
    pattern="deepfry(?: |$)([1-9])?",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    level = int(match) if match else 1
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
    fry_image = Root / "downloads/fry.jpeg"
    if isinstance(reply.media, MessageMediaPhoto):
        file = fry_image
    else:
        mim = reply.media.document.mime_type
        ext = mimetypes.guess_extension(mim)
        file = Root / ("downloads/" + f"fry{ext}")
    await kst.client.download_media(data, file=file)
    if ext and ext in (".mp4", ".gif", ".webm"):
        to_deepfry = fry_image
        ss = await Screenshot(file, 0, fry_image)
        if not ss:
            (file).unlink(missing_ok=True)
            return await yy.try_delete()
    else:
        to_deepfry = file
    try:
        for _ in range(level):
            img = await deepfry(to_deepfry)
        img.save(fry_image, format="JPEG")
    except BaseException:
        (to_deepfry).unlink(missing_ok=True)
        return await yy.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=fry_image,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await yy.try_delete()
    (file).unlink(missing_ok=True)
    (fry_image).unlink(missing_ok=True)


async def conv_fry(conv, image, level):
    try:
        resp = conv.wait_event(NewMessage(incoming=True, from_users=conv.chat_id))
        media = await conv.send_file(
            image,
            force_document=False,
            allow_cache=False,
        )
        resp = await resp
        await resp.try_delete()
        yy = await conv.send_message(f"/deepfry {level}", reply_to=media.id)
        resp = conv.wait_event(NewMessage(incoming=True, from_users=conv.chat_id))
        resp = await resp
        await yy.try_delete()
        await resp.mark_read(clear_mentions=True)
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client(UnblockRequest(conv.chat_id))
        return await conv_fry(conv, image, level)


@make_async
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
    img = ImageEnhance.Sharpness(img).enhance(random.randint(5, 300))
    return img


def check_media(reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if DocumentAttributeFilename(file_name="AnimatedSticker.tgs") in reply.media.document.attributes:
                return False
            if reply.audio or reply.voice:
                return False
            data = reply.media.document
        else:
            return False
    if not data or data is None:
        return False
    return data


plugins_help["deepfry"] = {
    "{i}fry [1-8] [reply]": "Frying any image/sticker/gif/video use image_deepfrybot (default level 3).",
    "{i}deepfry [1-9] [reply]": "Deepfy any image/sticker/gif/video and make it look ugly (default level 1).",
}
