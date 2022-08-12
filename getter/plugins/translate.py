# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from gpytranslate import Translator
from gtts import gTTS
from . import (
    Root,
    HELP,
    hl,
    kasta_cmd,
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
    args = kst.pattern_match.group(1)
    lang = args[:2] or "id"
    txt = args[3:]
    text = ""
    msg = await kst.eor("`...`")
    if txt:
        text = txt
    elif kst.is_reply:
        text = (await kst.get_reply_message()).text
    if not text:
        await msg.eod(f"`{hl}tr <lang code>` reply text message.")
        return
    try:
        text = strip_format(strip_emoji(text))
        translator = Translator()
        translation = await translator(text, targetlang=lang)
        after_tr_text = translation.text
        source_lang = await translator.detect(translation.orig)
        transl_lang = await translator.detect(translation.text)
        output_text = "**Detected:** `{}`\n**Translated:** `{}`\n\n```{}```".format(
            source_lang,
            transl_lang,
            after_tr_text,
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
    args = kst.pattern_match.group(1)
    lang = args[:2] or "id"
    txt = args[3:]
    text = ""
    if txt:
        text = txt
    elif kst.is_reply:
        text = (await kst.get_reply_message()).text
    if not text:
        await kst.eod(f"`{hl}tl <lang code>` reply text message.")
        return
    try:
        text = strip_format(strip_emoji(text))
        translator = Translator()
        tl = (await translator(text, targetlang=lang)).text
        await kst.sod(tl)
    except Exception as err:
        return await kst.eod(str(err), parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"tts(?: |$)([\s\S]*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    args = kst.pattern_match.group(1)
    lang = args[:2] or "id"
    txt = args[3:]
    text = ""
    msg = await kst.eor("`...`")
    if txt:
        text = txt
    elif kst.is_reply:
        text = (await kst.get_reply_message()).text
    if not text:
        await msg.eod(f"`{hl}tts <lang code>` reply text message.")
        return
    try:
        text = strip_format(strip_emoji(text))
        file = Root / ("downloads/" + "tts.mp3")
        tts = gTTS(text, lang=lang, slow=False)
        tts.save(file)
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            reply_to=kst.reply_to_msg_id or None,
            allow_cache=False,
            voice_note=True,
            silent=True,
        )
        (file).unlink(missing_ok=True)
        await msg.try_delete()
    except Exception as err:
        await msg.eod(str(err), parse_mode=parse_pre)


HELP.update(
    {
        "translate": [
            "Translate",
            """❯ `{i}tr <lang code> <text/reply>`
Translate the message to required language.

❯ `{i}tl <lang code> <text/reply>`
Send or reply message as translated.

❯ `{i}tts <lang code> <text/reply>`
Text to speech.

**Note:** Default <lang code> is `id`.
""",
        ]
    }
)
