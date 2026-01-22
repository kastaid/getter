# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from random import choice

from . import (
    CARBON_PRESETS,
    RAYSO_THEMES,
    Carbon,
    Root,
    get_media_type,
    kasta_cmd,
    mentionuser,
    plugins_help,
)


@kasta_cmd(
    pattern=r"carbon(?: |$)([\s\S]*)",
)
async def _(kst):
    ga = kst.client
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in CARBON_PRESETS:
        is_theme, theme = True, args[0]
    else:
        is_theme, theme = False, choice(tuple(CARBON_PRESETS))
    if kst.is_reply:
        reply = await kst.get_reply_message()
        if reply.media and get_media_type(reply.media) == "text":
            file = await reply.download_media()
            code = (Root / file).read_text()
            (Root / file).unlink(missing_ok=True)
        else:
            code = reply.message
        if is_theme:
            try:
                code = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    else:
        code = match
        if is_theme:
            try:
                code = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    if not code:
        return await kst.eod("`Reply to text message or readable file.`")
    yy = await kst.eor("`Processing...`")
    backgroundColor = CARBON_PRESETS[theme]
    windowTheme = choice(("none", "sharp", "bw"))
    carbon = await Carbon(
        code.strip(),
        file_name="carbon",
        download=True,
        fontFamily="Fira Code",
        theme=theme,
        backgroundColor=backgroundColor,
        dropShadow=windowTheme != "bw",
        windowTheme=windowTheme,
    )
    if not carbon:
        return await yy.eod("`Carbon API not responding.`")
    await yy.eor(
        f"Carboniz by {mentionuser(ga.uid, ga.full_name, html=True)}",
        file=carbon,
        parse_mode="html",
        force_document=False,
    )
    (Root / carbon).unlink(missing_ok=True)


@kasta_cmd(
    pattern=r"rayso(?: |$)([\s\S]*)",
)
async def _(kst):
    ga = kst.client
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in RAYSO_THEMES:
        is_theme, theme = True, args[0]
    else:
        is_theme, theme = False, choice(RAYSO_THEMES)
    if kst.is_reply:
        reply = await kst.get_reply_message()
        if reply.media and get_media_type(reply.media) == "text":
            file = await reply.download_media()
            code = (Root / file).read_text()
            (Root / file).unlink(missing_ok=True)
        else:
            code = reply.message
        if is_theme:
            try:
                code = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    else:
        code = match
        if is_theme:
            try:
                code = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    if not code:
        return await kst.eod("`Reply to text message or readable file.`")
    yy = await kst.eor("`Processing...`")
    darkMode = choice((True, False))
    rayso = await Carbon(
        code,
        file_name="rayso",
        download=True,
        rayso=True,
        theme=theme,
        darkMode=darkMode,
    )
    if not rayso:
        return await yy.eod("`Rayso API not responding.`")
    await yy.eor(
        f"Raysoniz by {mentionuser(ga.uid, ga.full_name, html=True)}",
        file=rayso,
        parse_mode="html",
        force_document=False,
    )
    (Root / rayso).unlink(missing_ok=True)


@kasta_cmd(
    pattern="theme$",
)
async def _(kst):
    carbon = f"**{len(CARBON_PRESETS)} Carbon Themes:**\n" + "\n".join([f"- `{_}`" for _ in CARBON_PRESETS])
    rayso = f"**{len(RAYSO_THEMES)} Rayso Themes:**\n" + "\n".join([f"- `{_}`" for _ in RAYSO_THEMES])
    await kst.sod(carbon)
    await kst.sod(rayso)


plugins_help["beautify"] = {
    "{i}carbon [theme] [text]/[reply (text or readable file)]": "Carboniz the text with choosing theme or random themes.",
    "{i}rayso [theme] [text]/[reply (text or readable file)]": "Raysoniz the text with choosing theme or random themes.",
    "{i}theme": "List all themes name.",
}
