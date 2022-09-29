# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from gpytranslate import Translator
from gtts import gTTS
from . import (
    Root,
    Var,
    kasta_cmd,
    plugins_help,
    LANG_CODES,
    suppress,
    format_exc,
    strip_format,
    strip_emoji,
    strip_ascii,
    sort_dict,
    aioify,
)


@kasta_cmd(
    pattern="tr(?: |$)((?s).*)",
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
            with suppress(BaseException):
                words = match.split(maxsplit=1)[1]
    else:
        words = match
        if is_lang:
            with suppress(BaseException):
                words = match.split(maxsplit=1)[1]
    if not words:
        await kst.eor("`Reply to text message or provide a text!`", time=5)
        return
    yy = await kst.eor("`...`")
    try:
        text = strip_format(strip_emoji(words))
        translator = Translator()
        translation = await translator(text, targetlang=lang)
        tr = "**Detected:** `{}`\n**Translated:** `{}`\n\n```{}```".format(
            await translator.detect(translation.orig),
            await translator.detect(translation.text),
            translation.text,
        )
        await yy.eor(tr, parts=True)
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="tl(?: |$)((?s).*)",
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
            with suppress(BaseException):
                words = match.split(maxsplit=1)[1]
    else:
        words = match
        if is_lang:
            with suppress(BaseException):
                words = match.split(maxsplit=1)[1]
    if not words:
        await kst.eor("`Reply to text message or provide a text!`", time=5)
        return
    try:
        text = strip_format(strip_emoji(words))
        translation = await Translator()(text, targetlang=lang)
        await kst.sod(translation.text, parts=True)
    except Exception as err:
        await kst.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="t(t|)s(?: |$)((?s).*)",
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
            with suppress(BaseException):
                words = match.split(maxsplit=1)[1]
    else:
        words = match
        if is_lang:
            with suppress(BaseException):
                words = match.split(maxsplit=1)[1]
    if not words:
        await kst.eor("`Reply to text message or provide a text!`", time=5)
        return
    yy = await kst.eor("`...`")
    try:
        text = strip_ascii(strip_format(strip_emoji(words)))
        if kst.pattern_match.group(1).strip() != "t":
            text = (await Translator()(text, targetlang=lang)).text
        file = Root / "downloads/voice.mp3"
        voice = await aioify(gTTS, text, lang=lang, slow=False)
        voice.save(file)
        await yy.eor(
            file=file,
            allow_cache=False,
            voice_note=True,
        )
        (file).unlink(missing_ok=True)
    except Exception as err:
        await yy.eor(format_exc(err), parse_mode="html")


@kasta_cmd(
    pattern="lang$",
)
async def _(kst):
    lang = f"**{len(LANG_CODES)} Language Code:**\n" + "\n".join(
        [f"- {y}: {x}" for x, y in sort_dict(LANG_CODES).items()]
    )
    await kst.sod(lang, parts=True)


plugins_help["translate"] = {
    "{i}tr [lang_code] [text]/[reply]": f"Translate the message to required language. Default lang_code for all is `{Var.LANG_CODE}`.",
    "{i}tl [lang_code] [text]/[reply]": "Send or reply message as translated.",
    "{i}tts [lang_code] [text]/[reply]": "Text to speech.",
    "{i}ts [lang_code] [text]/[reply]": "Translate the message then text to speech.",
    "{i}lang": """List all language code.

**Examples:**
- Use default lang_code.
-> `{i}tr ready`
- With choosing lang_code.
-> `{i}tr en siap`

- Translate the replied message.
-> `{i}tr [reply]`
-> `{i}tr en [reply]`
- Reply a message with translated text (must have lang_code).
-> `{i}tr en siap`

Examples above both for all commands!
""",
}
