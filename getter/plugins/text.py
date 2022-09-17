# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import base64
import re
import string
from . import (
    kasta_cmd,
    plugins_help,
    parse_pre,
    strip_format,
    strip_emoji,
    camel,
    snake,
    kebab,
    FLIP_MAP,
    Fetch,
)


@kasta_cmd(
    pattern="getformat$",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    reply = await kst.get_reply_message()
    if not getattr(reply, "text", None):
        return await kst.try_delete()
    text = reply.text
    await kst.eor(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern="noformat$",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    reply = await kst.get_reply_message()
    if not getattr(reply, "message", None):
        return await kst.try_delete()
    text = strip_format(reply.message)
    await kst.eor(text)


@kasta_cmd(
    pattern="nospace$",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    reply = await kst.get_reply_message()
    if not getattr(reply, "text", None):
        return await kst.try_delete()
    text = "".join(reply.text.split())
    await kst.eor(text)


@kasta_cmd(
    pattern="noemoji$",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    reply = await kst.get_reply_message()
    if not getattr(reply, "text", None):
        return await kst.try_delete()
    text = strip_emoji(reply.text)
    await kst.eor(text)


@kasta_cmd(
    pattern="repeat(?: |$)(.*)",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    count = kst.pattern_match.group(1)
    reply = await kst.get_reply_message()
    if not getattr(reply, "text", None):
        return await kst.try_delete()
    count = int(count) if count.isdecimal() else 1
    txt = reply.text
    text = txt + "\n"
    for _ in range(count - 1):
        text += txt + "\n"
    await kst.eor(text)


@kasta_cmd(
    pattern=r"count(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst)
    if not text:
        return await kst.try_delete()
    count = len(re.findall(r"(\S+)", text))
    text = f"**Count:** `{count}`"
    await kst.eor(text)


@kasta_cmd(
    pattern=r"(upper|lower|title|capital|camel|snake|kebab)(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2, plain=False)
    if not text:
        return await kst.try_delete()
    cmd = kst.pattern_match.group(1)
    if cmd == "upper":
        text = text.upper()
    elif cmd == "lower":
        text = text.lower()
    elif cmd == "title":
        text = text.title()
    elif cmd == "capital":
        text = text.capitalize()
    elif cmd == "camel":
        text = camel(text)
    elif cmd == "snake":
        text = snake(text)
    elif cmd == "kebab":
        text = kebab(text)
    await kst.eor(text)


@kasta_cmd(
    pattern="(b64encode|b64e)(?: |$)(.*)",
    no_crash=False,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    text = base64.b64encode(text.encode("utf-8")).decode()
    await kst.eor(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern="(b64decode|b64d)(?: |$)(.*)",
    no_crash=False,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    try:
        text = base64.b64decode(text).decode("utf-8", "replace")
    except Exception as err:
        text = f"Invalid Base64 data: {err}"
    await kst.eor(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern="(morse|unmorse)(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    cmd = kst.pattern_match.group(1)
    api = "en" if cmd == "morse" else "de"
    yy = await kst.eor("`...`")
    text = text.encode("utf-8")
    url = f"https://notapi.vercel.app/api/morse?{api}={text}"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.eor(res.get("result"))


@kasta_cmd(
    pattern="(roman|unroman)(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    cmd = kst.pattern_match.group(1)
    api = "en" if cmd == "roman" else "de"
    yy = await kst.eor("`...`")
    text = text.encode("utf-8")
    url = f"https://notapi.vercel.app/api/romans?{api}={text}"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.eor(res.get("result"))


@kasta_cmd(
    pattern=r"(spoiler|sp)(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2, plain=False)
    if not text:
        return await kst.try_delete()
    text = f"||{text}||"
    await kst.eor(text)


@kasta_cmd(
    pattern=r"type(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    match = await kst.client.get_text(kst)
    if not match:
        return await kst.try_delete()
    text = "\u2060" * 602
    yy = await kst.eor(text)
    typing_symbol = "|"
    prev_text = ""
    await yy.eor(typing_symbol)
    await asyncio.sleep(0.4)
    for c in match:
        prev_text = prev_text + "" + c
        typing_text = prev_text + "" + typing_symbol
        await yy.eor(typing_text)
        await asyncio.sleep(0.4)
        await yy.eor(prev_text)
        await asyncio.sleep(0.4)


@kasta_cmd(
    pattern=r"flip(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst, plain=False)
    if not text:
        return await kst.try_delete()
    text = "  ".join(text)
    final_text = ""
    for char in text:
        new_char = FLIP_MAP.get(char, char)
        final_text += new_char
    if text != final_text:
        return await kst.eor(final_text)
    await kst.eor(text)


@kasta_cmd(
    pattern=r"small(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    text = await kst.client.get_text(kst)
    if not text:
        return await kst.try_delete()
    small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀsᴛᴜᴠᴡxʏᴢ"
    text = text.lower().translate(str.maketrans(string.ascii_lowercase, small_caps))
    await kst.eor(text)


plugins_help["text"] = {
    "{i}getformat [reply]": "Get a replied message format.",
    "{i}noformat [reply]": "Clean format in replied message.",
    "{i}nospace [reply]": "Remove all spaces in replied message.",
    "{i}noemoji [reply]": "Remove all emoji in replied message.",
    "{i}repeat [count] [reply]": "Repeat text in replied message.",
    "{i}count [text]/[reply]": "Count words in text message.",
    "{i}upper [text]/[reply]": "Convert text to UPPERCASE.",
    "{i}lower [text]/[reply]": "Convert text to lowercase.",
    "{i}title [text]/[reply]": "Convert text to TitleCase.",
    "{i}capital [text]/[reply]": "Convert first word to Capital.",
    "{i}camel [text]/[reply]": "Convert text to camelCase.",
    "{i}snake [text]/[reply]": "Convert text to snake_case.",
    "{i}kebab [text]/[reply]": "Convert text to kebab-case.",
    "{i}b64encode|{i}b64e [text]/[reply]": "Encode text into Base64.",
    "{i}b64decode|{i}b64d [text]/[reply]": "Decode Base64 data.",
    "{i}morse [text]/[reply]": "Encode text into Morse code.",
    "{i}unmorse [text]/[reply]": "Decode Morse code.",
    "{i}roman [text]/[reply]": "Convert any number less than 4000 to roman numerals.",
    "{i}unroman [text]/[reply]": "Convert roman numeral to number.",
    "{i}spoiler|{i}sp [text]/[reply]": "Create a spoiler message.",
    "{i}type [text]/[reply]": "Edits the message and shows like someone is typing.",
    "{i}flip [text]/[reply]": "Flip text upside down.",
    "{i}small [text]/[reply]": "Make caps text smaller.",
}
