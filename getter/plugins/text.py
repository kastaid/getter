# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import base64
import re
from string import ascii_lowercase

from . import (
    FLIP_MAP,
    Fetch,
    camel,
    formatx_send,
    kasta_cmd,
    kebab,
    normalize,
    parse_pre,
    plugins_help,
    snake,
    strip_emoji,
    strip_format,
)


@kasta_cmd(
    pattern=r"getformat(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, plain=False)
    if not text:
        return await kst.try_delete()
    await kst.eor(text, parts=True, parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"noformat(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst)
    if not text:
        return await kst.try_delete()
    text = strip_format(text)
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern=r"nospace(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, plain=False)
    if not text:
        return await kst.try_delete()
    text = "".join(text.split())
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern=r"noemoji(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, plain=False)
    if not text:
        return await kst.try_delete()
    text = strip_emoji(text)
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern="repeat(?: |$)(.*)",
    func=lambda e: e.is_reply,
)
async def _(kst):
    count = kst.pattern_match.group(1)
    reply = await kst.get_reply_message()
    if not getattr(reply, "text", None):
        return await kst.try_delete()
    count = int(count) if count.isdecimal() else 1
    orig = reply.text
    text = orig + "\n"
    for _ in range(count - 1):
        text += orig + "\n"
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern=r"count(?: |$)([\s\S]*)",
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
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern=r"b64(encode|en|e)(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    yy = await kst.eor("`...`")
    text = base64.b64encode(text.encode("utf-8")).decode()
    await yy.sod(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern="b64(decode|de|d)(?: |$)(.*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    yy = await kst.eor("`...`")
    try:
        text = base64.b64decode(text).decode("utf-8", "replace")
    except Exception as err:
        return await yy.eor(formatx_send(err), parse_mode="html")
    await yy.sod(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"(to|no)bin(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    yy = await kst.eor("`...`")
    cmd = kst.pattern_match.group(1)
    if cmd == "to":
        text = " ".join(f"{ord(_):08b}" for _ in text)
    else:
        text = "".join([chr(int(_, 2)) for _ in text.split(" ")])
    await yy.sod(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern="(no|)morse(?: |$)(.*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    yy = await kst.eor("`...`")
    cmd = kst.pattern_match.group(1).strip()
    api = "de" if cmd == "no" else "en"
    text = text.encode("utf-8")
    url = f"https://notapi.vercel.app/api/morse?{api}={text}"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.sod(res.get("result"))


@kasta_cmd(
    pattern="(no|)roman(?: |$)(.*)",
)
async def _(kst):
    text = await kst.client.get_text(kst, group=2)
    if not text:
        return await kst.try_delete()
    yy = await kst.eor("`...`")
    cmd = kst.pattern_match.group(1).strip()
    api = "de" if cmd == "no" else "en"
    text = text.encode("utf-8")
    url = f"https://notapi.vercel.app/api/romans?{api}={text}"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.sod(res.get("result"))


@kasta_cmd(
    pattern=r"type(?: |$)([\s\S]*)",
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
    await asyncio.sleep(0.3)
    for c in match:
        prev_text = prev_text + "" + c
        typing_text = prev_text + "" + typing_symbol
        await yy.eor(typing_text)
        await asyncio.sleep(0.3)
        await yy.eor(prev_text)
        await asyncio.sleep(0.3)


@kasta_cmd(
    pattern=r"flip(?: |$)([\s\S]*)",
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
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern=r"small(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst)
    if not text:
        return await kst.try_delete()
    small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀsᴛᴜᴠᴡxʏᴢ"
    text = text.lower().translate(str.maketrans(ascii_lowercase, small_caps))
    await kst.eor(text, parts=True)


@kasta_cmd(
    pattern=r"normal(?: |$)([\s\S]*)",
)
async def _(kst):
    text = await kst.client.get_text(kst)
    if not text:
        return await kst.try_delete()
    text = normalize(text).upper()
    await kst.eor(text, parts=True)


plugins_help["text"] = {
    "{i}getformat [text]/[reply]": "Get a replied message format.",
    "{i}noformat [text]/[reply]": "Clean format in replied message.",
    "{i}nospace [text]/[reply]": "Remove all spaces in replied message.",
    "{i}noemoji [text]/[reply]": "Remove all emoji in replied message.",
    "{i}repeat [count] [reply]": "Repeat text in replied message.",
    "{i}count [text]/[reply]": "Count words in text message.",
    "{i}upper [text]/[reply]": "Convert text to UPPERCASE.",
    "{i}lower [text]/[reply]": "Convert text to lowercase.",
    "{i}title [text]/[reply]": "Convert text to TitleCase.",
    "{i}capital [text]/[reply]": "Convert first word to Capital.",
    "{i}camel [text]/[reply]": "Convert text to camelCase.",
    "{i}snake [text]/[reply]": "Convert text to snake_case.",
    "{i}kebab [text]/[reply]": "Convert text to kebab-case.",
    "{i}b64encode|{i}b64en|{i}b64e [text]/[reply]": "Encode and convert text to base64 data.",
    "{i}b64decode|{i}b64de|{i}b64d [text]/[reply]": "Decode and convert base64 data to text.",
    "{i}tobin [text]/[reply]": "Encode and convert text to binary.",
    "{i}nobin [text]/[reply]": "Decode and convert binary to text.",
    "{i}morse [text]/[reply]": "Encode and convert text to morse code.",
    "{i}nomorse [text]/[reply]": "Decode and convert morse code to text.",
    "{i}roman [text]/[reply]": "Convert any number less than 4000 to roman numerals.",
    "{i}noroman [text]/[reply]": "Convert roman numeral to number.",
    "{i}type [text]/[reply]": "Edits the message and shows like someone is typing.",
    "{i}flip [text]/[reply]": "Flip text upside down.",
    "{i}small [text]/[reply]": "Make caps text smaller.",
    "{i}normal [text]/[reply]": "Convert stylish font to normal.",
}
