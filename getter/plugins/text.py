# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from base64 import b64encode, b64decode
from binascii import Error as AsciiError
from re import sub, findall
from . import (
    HELP,
    kasta_cmd,
    parse_pre,
    Searcher,
)


def camel(s: str) -> str:
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    return "".join([s[0].lower(), s[1:]])


def snake(s: str) -> str:
    return "_".join(sub("([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", s.replace("-", " "))).split()).lower()


def kebab(s: str) -> str:
    return "-".join(
        sub(
            r"(\s|_|-)+",
            " ",
            sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda mo: " " + mo.group(0).lower(),
                s,
            ),
        ).split()
    )


@kasta_cmd(disable_errors=True, pattern="noformat$")
async def _noformat(e):
    rep = await e.get_reply_message()
    if not e.is_reply or not (hasattr(rep, "text") and rep.text):
        return await e.try_delete()
    await e.eor(rep.text, parse_mode=parse_pre)


@kasta_cmd(disable_errors=True, pattern="nospace$")
async def _nospace(e):
    rep = await e.get_reply_message()
    if not e.is_reply or not (hasattr(rep, "text") and rep.text):
        return await e.try_delete()
    await e.eor("".join(rep.text.split()))


@kasta_cmd(disable_errors=True, pattern="repeat(?: |$)(.*)")
async def _repeat(e):
    count = e.pattern_match.group(1)
    rep = await e.get_reply_message()
    if not e.is_reply or not (hasattr(rep, "text") and rep.text):
        return await e.try_delete()
    count = int(count) if count.isdecimal() else 1
    txt = rep.text
    text = txt + "\n"
    for _ in range(0, count - 1):
        text += txt + "\n"
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"count(?:\s|$)([\s\S]*)")
async def _count(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    count = len(findall(r"(\S+)", Kst))
    text = f"**Count:** `{count}`"
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"upper(?:\s|$)([\s\S]*)")
async def _upper(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = Kst.upper()
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"lower(?:\s|$)([\s\S]*)")
async def _lower(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = Kst.lower()
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"title(?:\s|$)([\s\S]*)")
async def _title(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = Kst.title()
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"capital(?:\s|$)([\s\S]*)")
async def _capital(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = Kst.capitalize()
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"camel(?:\s|$)([\s\S]*)")
async def _camel(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = camel(Kst)
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"snake(?:\s|$)([\s\S]*)")
async def _snake(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = snake(Kst)
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern=r"kebab(?:\s|$)([\s\S]*)")
async def _kebab(e):
    Kst = e.pattern_match.group(1)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = kebab(Kst)
    await e.eor(text)


@kasta_cmd(disable_errors=True, pattern="(b64encode|b64e)(?: |$)(.*)")
async def _b64encode(e):
    Kst = e.pattern_match.group(2)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    text = b64encode(Kst.encode("utf-8")).decode()
    await e.eor(text, parse_mode=parse_pre)


@kasta_cmd(disable_errors=True, pattern="(b64decode|b64d)(?: |$)(.*)")
async def _b64decode(e):
    Kst = e.pattern_match.group(2)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    try:
        text = b64decode(Kst).decode("utf-8", "replace")
    except AsciiError as err:
        text = f"Invalid Base64 data: {err}"
    await e.eor(text, parse_mode=parse_pre)


@kasta_cmd(disable_errors=True, pattern="(morse|unmorse)(?: |$)(.*)")
async def _morse(e):
    cmd = e.pattern_match.group(1)
    Kst = e.pattern_match.group(2)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    _ = "encode" if cmd == "morse" else "decode"
    msg = await e.eor("`...`")
    base_url = f"https://apis.xditya.me/morse/{_}?text=" + Kst
    text = await Searcher(base_url, re_content=False)
    if not text:
        return await msg.eod("`Try again now!`")
    await msg.eor(text)


@kasta_cmd(disable_errors=True, pattern="(roman|unroman)(?: |$)(.*)")
async def _roman(e):
    Kst = e.pattern_match.group(2)
    if not Kst and e.is_reply:
        Kst = (await e.get_reply_message()).text
    if not Kst:
        return await e.try_delete()
    msg = await e.eor("`...`")
    base_url = "https://romans.justyy.workers.dev/api/romans/?cached&n=" + Kst
    text = await Searcher(base_url, re_json=True)
    if not text:
        return await msg.eod("`Try again now!`")
    text = str(text.get("result"))
    await msg.eor(text)


HELP.update(
    {
        "text": [
            "Text",
            """❯ `{i}noformat <reply>`
Convert replied message without format.

❯ `{i}nospace <reply>`
Remove all spaces in text.

❯ `{i}repeat <count> <reply>`
Repeat text in replied message.

❯ `{i}count <text/reply>`
Count words in text message.

❯ `{i}upper <text/reply>`
Convert text to upper case.

❯ `{i}lower <text/reply>`
Convert text to lower case.

❯ `{i}title <text/reply>`
Convert text to title case.

❯ `{i}capital <text/reply>`
Convert first word to capital.

❯ `{i}camel <text/reply>`
Convert text to camel case.

❯ `{i}snake <text/reply>`
Convert text to snake case.

❯ `{i}kebab <text/reply>`
Convert text to kebab case.

❯ `{i}b64encode|{i}b64e <text/reply>`
Encode text into Base64.

❯ `{i}b64decode|{i}b64d <text/reply>`
Decode Base64 data.

❯ `{i}morse <text/reply>`
Encode text into Morse code.

❯ `{i}unmorse <text/reply>`
Decode Morse code.

❯ `{i}roman <text/reply>`
Convert an number to roman numeral.

❯ `{i}unroman <text/reply>`
Convert roman numeral to number.
""",
        ]
    }
)
