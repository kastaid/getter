# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import aiofiles
from . import (
    Root,
    kasta_cmd,
    plugins_help,
    choice,
    suppress,
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
    if kst.is_reply:
        reply = await kst.get_reply_message()
        if reply.media and bool([x for x in ("text", "application") if x in get_doc_mime(reply.media)]):
            file = await kst.client.download_media(reply)
            code = None
            async with aiofiles.open(file, mode="r") as f:
                code = await f.read()
            if not code:
                return await kst.try_delete()
            (Root / file).unlink(missing_ok=True)
        else:
            code = reply.text
    else:
        code = kst.pattern_match.group(1)
    if not code:
        return await kst.eod("`Reply to text message or readable file.`")
    msg = await kst.eor("`Processing...`")
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
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await msg.try_delete()
    (Root / carbon).unlink(missing_ok=True)


@kasta_cmd(
    pattern=r"rayso(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in RAYSO_THEMES:
        is_theme, theme = True, args[0]
    else:
        is_theme, theme = False, choice(RAYSO_THEMES)
    if kst.is_reply:
        reply = await kst.get_reply_message()
        if reply.media and bool([x for x in ("text", "application") if x in get_doc_mime(reply.media)]):
            file = await kst.client.download_media(reply)
            code = None
            async with aiofiles.open(file, mode="r") as f:
                code = await f.read()
            if not code:
                return await kst.try_delete()
            (Root / file).unlink(missing_ok=True)
        else:
            code = reply.text
        from_user = reply.sender
    else:
        try:
            code = match.split(maxsplit=1)[1] if is_theme else match
        except IndexError:
            code = match
        from_user = await kst.client.get_entity("me")
    if not code:
        return await kst.eod("`Reply to text message or readable file.`")
    msg = await kst.eor("`Processing...`")
    title = display_name(from_user)
    darkMode = choice((True, False))
    rayso = await Carbon(
        code,
        file_name="rayso",
        download=True,
        rayso=True,
        title=title,
        theme=theme,
        darkMode=darkMode,
    )
    if not rayso:
        return await msg.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=rayso,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await msg.try_delete()
    (Root / rayso).unlink(missing_ok=True)


plugins_help["beautify"] = {
    "{i}carbon [text/reply (text or readable file)]": "Carbonise the text with random presets.",
    "{i}rayso [theme] [text/reply (text or readable file)]": """Beauty showcase the text by Rayso with choosing theme or random themes.

**Rayso Themes:**
- `breeze`
- `candy`
- `crimson`
- `falcon`
- `meadow`
- `midnight`
- `raindrop`
- `sunset`""",
}
