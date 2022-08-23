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
    parse_pre,
    strip_format,
    strip_emoji,
)


@kasta_cmd(
    pattern=r"tr(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES.keys():
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, "id"
    if kst.is_reply:
        words = (await kst.get_reply_message()).text
    else:
        try:
            words = match.split(maxsplit=1)[1] if is_lang else match
        except IndexError:
            words = match
    if not words:
        await kst.eor("`Reply to text message or provide a text!`", time=5)
        return
    msg = await kst.eor("`...`")
    try:
        text = strip_format(strip_emoji(words))
        translator = Translator()
        translation = await translator(text, targetlang=lang)
        output_text = "**Detected:** `{}`\n**Translated:** `{}`\n\n```{}```".format(
            await translator.detect(translation.orig),
            await translator.detect(translation.text),
            translation.text,
        )
        await msg.eor(output_text)
    except Exception as err:
        await msg.eor(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"tl(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
@kasta_cmd(
    pattern=r"tl(?: |$)([\s\S]*)",
    no_handler=True,
    edited=True,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES.keys():
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, "id"
    if kst.is_reply:
        words = (await kst.get_reply_message()).text
    else:
        try:
            words = match.split(maxsplit=1)[1] if is_lang else match
        except IndexError:
            words = match
    if not words:
        await kst.eor("`Reply to text message or provide a text!`", time=5)
        return
    try:
        text = strip_format(strip_emoji(words))
        translator = Translator()
        translation = await translator(text, targetlang=lang)
        await kst.sod(translation.text)
    except Exception as err:
        return await kst.eod(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"tts(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    args = match.split(" ")
    if args[0] in LANG_CODES.keys():
        is_lang, lang = True, args[0]
    else:
        is_lang, lang = False, "id"
    if kst.is_reply:
        words = (await kst.get_reply_message()).text
    else:
        try:
            words = match.split(maxsplit=1)[1] if is_lang else match
        except IndexError:
            words = match
    if not words:
        await kst.eor("`Reply to text message or provide a text!`", time=5)
        return
    msg = await kst.eor("`...`")
    try:
        text = strip_format(strip_emoji(words))
        file = Root / ("downloads/" + "voice.mp3")
        voice = gTTS(text, lang=lang, slow=False)
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
        await msg.try_delete()
    except Exception as err:
        await msg.eod(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern="lang$",
    no_crash=True,
)
async def _(kst):
    lang = "**Language Code:**\n" + "\n".join([f"- {y}: {x}" for x, y in LANG_CODES.items()])
    await kst.sod(lang)


plugins_help["translate"] = {
    "{i}tr [lang_code] [text/reply]": "Translate the message to required language.",
    "{i}tl [lang_code] [text/reply]": "Send or reply message as translated.",
    "{i}tts [lang_code] [text/reply]": "Text to speech",
    "{i}lang": """Show all language code.

**Note:** Default [lang_code] is `id`.""",
}
