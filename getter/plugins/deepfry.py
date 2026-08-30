# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import random
from mimetypes import guess_extension

from PIL import (
    Image,
    ImageEnhance,
    ImageOps,
)
from telethon.tl import types as typ

from . import (
    DOWNLOAD_DIR,
    Screenshot,
    import_lib,
    kasta_cmd,
    plugins_help,
)


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
    ugly_img = DOWNLOAD_DIR / "ugly.jpeg"
    if isinstance(reply.media, typ.MessageMediaPhoto):
        file = ugly_img
    else:
        mim = reply.media.document.mime_type
        ext = guess_extension(mim)
        file = DOWNLOAD_DIR / f"ugly{ext}"
    await reply.download_media(file=file)
    if ext and ext in {".mp4", ".gif", ".webm"}:
        to_ugly = ugly_img
        ss = await Screenshot(file, 0, ugly_img)
        if not ss:
            await asyncio.to_thread(file.unlink, missing_ok=True)
            return await yy.try_delete()
    else:
        if ext and ext == ".tgs":
            ugly_img = DOWNLOAD_DIR / "ugly.png"
            await asyncio.to_thread(tgs_to_png, file, ugly_img)
            await asyncio.to_thread(file.unlink, missing_ok=True)
            file = ugly_img
        to_ugly = file
    try:
        for _ in range(level):
            img = await asyncio.to_thread(uglying, to_ugly)
        img.save(ugly_img, format="JPEG")
    except BaseException:
        await asyncio.to_thread(to_ugly.unlink, missing_ok=True)
        return await yy.try_delete()
    await yy.eor(
        file=ugly_img,
        force_document=False,
    )
    await asyncio.to_thread(file.unlink, missing_ok=True)
    await asyncio.to_thread(ugly_img.unlink, missing_ok=True)


def get_lottie():
    try:
        return get_lottie.modules
    except AttributeError:
        try:
            import cairosvg  # noqa
            from lottie.exporters import exporters
            from lottie.importers import importers
        except ImportError:
            import_lib(
                lib_name="lottie",
                pkg_name="lottie==0.7.2",
            )
            import_lib(
                lib_name="cairosvg",
                pkg_name="CairoSVG==2.9.0",
            )
            from lottie.exporters import exporters
            from lottie.importers import importers
        get_lottie.modules = importers, exporters
        return get_lottie.modules


def tgs_to_png(source, output):
    importers, exporters = get_lottie()
    importer = next(i for i in importers if "tgs" in i.extensions)
    exporter = exporters.get_from_filename(str(output))
    animation = importer.process(str(source))
    exporter.process(animation, str(output))


def uglying(img: Image) -> Image:
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
    "{i}ugly [1-9] [reply]": "Uglying any image/sticker/animation/gif/video and make it look ugly (default level 1).",
}
