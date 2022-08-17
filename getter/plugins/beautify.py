# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from contextlib import suppress
from aiofiles import open as aiopen
from . import (
    choice,
    Root,
    HELP,
    kasta_cmd,
    display_name,
    get_doc_mime,
    Carbon,
    CARBON_PRESETS,
    RAYSO_THEMES,
)


@kasta_cmd(
    pattern=r"carbon(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if kst.is_reply:
        rep = await kst.get_reply_message()
        if rep.media and bool([x for x in ("text", "application") if x in get_doc_mime(rep.media)]):
            file = await kst.client.download_media(rep)
            code = None
            async with aiopen(file, mode="r") as f:
                code = await f.read()
            if not code:
                return await msg.try_delete()
            (Root / file).unlink(missing_ok=True)
        else:
            code = rep.message
    else:
        code = kst.pattern_match.group(1)
    if not code:
        return await msg.eod("`Reply to text message or readable file.`")
    theme, backgroundColor = choice(CARBON_PRESETS)
    windowTheme = choice(("none", "sharp", "bw"))
    carbon = await Carbon(
        code.strip(),
        file_name="carbon",
        download=True,
        fontFamily="Fira Code",
        theme=theme,
        backgroundColor=backgroundColor,
        dropShadow=True if windowTheme != "bw" else False,
        windowTheme=windowTheme,
    )
    if not carbon:
        return await msg.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=carbon,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id or kst.id,
            silent=True,
        )
    await msg.try_delete()
    (Root / carbon).unlink(missing_ok=True)


@kasta_cmd(
    pattern=r"rayso(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if kst.is_reply:
        rep = await kst.get_reply_message()
        if rep.media and bool([x for x in ("text", "application") if x in get_doc_mime(rep.media)]):
            file = await kst.client.download_media(rep)
            code = None
            async with aiopen(file, mode="r") as f:
                code = await f.read()
            if not code:
                return await msg.try_delete()
            (Root / file).unlink(missing_ok=True)
        else:
            code = rep.message
        from_user = rep.sender
    else:
        code = kst.pattern_match.group(1)
        from_user = await kst.client.get_entity("me")
    if not code:
        return await msg.eod("`Reply to text message or readable file.`")
    title = display_name(from_user)
    theme, dark = choice(RAYSO_THEMES), choice((True, False))
    rayso = await Carbon(
        code,
        file_name="rayso",
        download=True,
        rayso=True,
        title=title,
        theme=theme,
        darkMode=dark,
    )
    if not rayso:
        return await msg.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=rayso,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id or kst.id,
            silent=True,
        )
    await msg.try_delete()
    (Root / rayso).unlink(missing_ok=True)


HELP.update(
    {
        "beautify": [
            "Beautify",
            """❯ `{i}carbon <text/reply (text or readable file)>`
Carbonise the text with random presets.

❯ `{i}rayso <text/reply (text or readable file)>`
Beauty showcase the text by rayso with random themes.
""",
        ]
    }
)
