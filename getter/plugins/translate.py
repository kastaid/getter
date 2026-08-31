# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from io import BytesIO

from . import (
    DOWNLOAD_DIR,
    LANG_CODES,
    Var,
    formatx_send,
    import_lib,
    kasta_cmd,
    plugins_help,
    sort_dict,
    strip_ascii,
    strip_emoji,
    strip_format,
)


@kasta_cmd(
    pattern=r"tr(?: |$)([\s\S]*)",
    edited=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES:
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, Var.LANG_CODE
    if kst.is_reply:
        words = (await kst.get_reply_message()).message
        if is_lang:
            try:
                words = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    else:
        words = match
        if is_lang:
            try:
                words = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    if not words:
        return await kst.eor("`Reply to text message or provide a text!`", time=5)
    yy = await kst.eor("`...`")
    try:
        text = strip_format(strip_emoji(words))
        translator = get_translator()
        translation = await translator.translate(text, targetlang=lang)
        tr = f"**Detected**: `{await translator.detect(translation.orig)}`\n**Translated**: `{await translator.detect(translation.text)}`\n\n```{translation.text}```"
        await yy.eor(tr, parts=True)
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern=r"tl(?: |$)([\s\S]*)",
    edited=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES:
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, Var.LANG_CODE
    if kst.is_reply:
        words = (await kst.get_reply_message()).message
        if is_lang:
            try:
                words = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    else:
        words = match
        if is_lang:
            try:
                words = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    if not words:
        return await kst.eor("`Reply to text message or provide a text!`", time=5)
    try:
        text = strip_format(strip_emoji(words))
        translator = get_translator()
        translation = await translator.translate(text, targetlang=lang)
        await kst.sod(translation.text, parts=True)
    except Exception as err:
        await kst.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern=r"t(t|)s(?: |$)([\s\S]*)",
    edited=True,
)
async def _(kst):
    match = kst.pattern_match.group(2)
    args = match.split(" ")
    if args[0] in LANG_CODES:
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, Var.LANG_CODE
    if kst.is_reply:
        words = (await kst.get_reply_message()).message
        if is_lang:
            try:
                words = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    else:
        words = match
        if is_lang:
            try:
                words = match.split(maxsplit=1)[1]
            except BaseException:
                pass
    if not words:
        return await kst.eor("`Reply to text message or provide a text!`", time=5)
    yy = await kst.eor("`...`")
    try:
        text = strip_ascii(strip_format(strip_emoji(words)))
        translator = get_translator()
        if kst.pattern_match.group(1).strip() != "t":
            text = (await translator.translate(text, targetlang=lang)).text
        file = DOWNLOAD_DIR / "voice.mp3"
        voice = BytesIO()
        await translator.tts(text, file=voice)
        await asyncio.to_thread(file.write_bytes, voice.getvalue())
        await yy.eor(
            file=file,
            voice_note=True,
        )
        await asyncio.to_thread(file.unlink, missing_ok=True)
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="lang$",
)
async def _(kst):
    lang = f"**{len(LANG_CODES)} Language Code**:\n" + "\n".join(
        [f"- {k}: {v}" for k, v in sort_dict(LANG_CODES).items()]
    )
    await kst.sod(lang, parts=True)


def get_translator():
    try:
        return get_translator.translator
    except AttributeError:
        try:
            from gpytranslate import Translator
        except ImportError:
            Translator = import_lib(
                lib_name="gpytranslate",
                pkg_name="gpytranslate==2.1.0",
            ).Translator
        get_translator.translator = Translator()
        return get_translator.translator


plugins_help["translate"] = {
    "{pfx}tr [lang_code] [text]/[reply]": f"Translate the message to required language. Default lang_code for all is `{Var.LANG_CODE}`.",
    "{pfx}tl [lang_code] [text]/[reply]": "Send or reply message as translated.",
    "{pfx}tts [lang_code] [text]/[reply]": "Text to speech.",
    "{pfx}ts [lang_code] [text]/[reply]": "Translate the message then text to speech.",
    "{pfx}lang": """List all language code.

**Examples**:
- Use default lang_code.
-> `{pfx}tr ready`
- With choosing lang_code.
-> `{pfx}tr en siap`

- Translate the replied message.
-> `{pfx}tr [reply]`
-> `{pfx}tr en [reply]`
- Reply a message with translated text (must have lang_code).
-> `{pfx}tr en siap`

Examples above both for all commands!
""",
}
