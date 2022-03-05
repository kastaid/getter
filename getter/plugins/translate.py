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
    md_to_text,
    deEmojify,
)


@kasta_cmd(disable_errors=True, pattern="tr")
async def _(e):
    if len(e.text) > 3 and e.text[3] != " ":
        await e.try_delete()
        return
    lang = e.text[4:6] or "id"
    txt = e.text[7:]
    Kst = await e.eor("`...`")
    if txt:
        text = txt
    elif e.is_reply:
        text = (await e.get_reply_message()).text
    if not text:
        await Kst.eor(f"`{hl}tr <lang code>` reply a text message.", time=15)
        return
    try:
        text = md_to_text(deEmojify(text.strip()))
        translator = Translator()
        translation = await translator(text, targetlang=lang)
        after_tr_text = translation.text
        source_lang = await translator.detect(translation.orig)
        transl_lang = await translator.detect(translation.text)
        output_str = "**Detected:** `{}`\n**Translated:** `{}`\n\n```{}```".format(
            source_lang,
            transl_lang,
            after_tr_text,
        )
        await Kst.eor(output_str)
    except Exception as err:
        await Kst.eor(str(err), parse_mode=parse_pre)


@kasta_cmd(disable_errors=True, pattern="tts")
async def _(e):
    if len(e.text) > 4 and e.text[4] != " ":
        return await e.try_delete()
    lang = e.text[5:7] or "id"
    txt = e.text[8:]
    Kst = await e.eor("`...`")
    if txt:
        text = txt
    elif e.is_reply:
        text = (await e.get_reply_message()).text
    if not text:
        await Kst.eor(f"`{hl}tts <lang code>` reply a text message.", time=15)
        return
    try:
        text = md_to_text(deEmojify(text.strip()))
        voice = Root / ("downloads/" + "tts.mp3")
        tts = gTTS(text, lang=lang, slow=False)
        tts.save(voice)
        await e.client.send_file(
            e.chat_id,
            file=voice,
            reply_to=e.reply_to_msg_id or None,
            allow_cache=False,
            voice_note=True,
        )
        (voice).unlink(missing_ok=True)
        await e.try_delete()
    except Exception as err:
        await Kst.eor(str(err), parse_mode=parse_pre)


HELP.update(
    {
        "translate": [
            "Translate",
            """❯ `{i}tr <lang code> <text/reply>`
Translate a languages.

❯ `{i}tts <lang code> <text/reply>`
Text to speech.

**Note:** Default <lang code> is `id`.
""",
        ]
    }
)
