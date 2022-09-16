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
    kasta_cmd,
    plugins_help,
    LANG_CODES,
    suppress,
    parse_pre,
    strip_format,
    strip_emoji,
    strip_ascii,
    sort_dict,
    aioify,
)

DEFAULT_LANG = "id"


@kasta_cmd(
    pattern=r"tr(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES:
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, DEFAULT_LANG
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
        await yy.eor(tr)
    except Exception as err:
        await yy.eod(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"tl(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES:
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, DEFAULT_LANG
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
        translator = Translator()
        translation = await translator(text, targetlang=lang)
        await kst.sod(translation.text)
    except Exception as err:
        await kst.eod(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"t(t|)s(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(2)
    args = match.split(" ")
    if args[0] in LANG_CODES:
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, DEFAULT_LANG
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
            translator = Translator()
            text = (await translator(text, targetlang=lang)).text
        file = Root / "downloads/voice.mp3"
        voice = await aioify(gTTS, text, lang=lang, slow=False)
        voice.save(file)
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            reply_to=kst.reply_to_msg_id,
            allow_cache=False,
            voice_note=True,
            silent=True,
        )
        (file).unlink(missing_ok=True)
        await yy.try_delete()
    except Exception as err:
        await yy.eod(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern="lang$",
    no_crash=True,
)
async def _(kst):
    lang = "**Language Code:**\n" + "\n".join([f"- {y}: {x}" for x, y in sort_dict(LANG_CODES).items()])
    await kst.sod(lang)


plugins_help["translate"] = {
    "{i}tr [lang_code] [text]/[reply]": f"Translate the message to required language. Default lang_code for all is `{DEFAULT_LANG}`.",
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
