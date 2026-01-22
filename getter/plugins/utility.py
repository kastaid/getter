# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import re
from datetime import datetime
from html import escape
from mimetypes import guess_extension

import aiofiles
from bs4 import BeautifulSoup
from PIL import Image
from telethon.tl import types as typ

from . import (
    TZ,
    Fetch,
    Root,
    Runner,
    Telegraph,
    aioify,
    formatx_send,
    get_media_type,
    get_msg_id,
    import_lib,
    kasta_cmd,
    normalize_chat_id,
    parse_pre,
    plugins_help,
    replace_all,
    sendlog,
)


@kasta_cmd(
    pattern=r"spcheck(?: |$)([\s\S]*)",
)
async def _(kst):
    ga = kst.client
    sentence = await ga.get_text(kst)
    if not sentence:
        return await kst.eor("`Provide a text/sentence!`", time=5)
    yy = await kst.eor("`Processing...`")
    try:
        from textblob import TextBlob
    except ImportError:
        TextBlob = import_lib(
            lib_name="textblob",
            pkg_name="TextBlob==0.17.1",
        ).TextBlob
    try:
        check = TextBlob(sentence)
        correct = check.correct()
    except Exception as err:
        return await yy.eor(formatx_send(err), parse_mode="html")
    text = f"• **Given Phrase:** `{sentence}`\n• **Corrected Phrase:** `{correct.strip()}`"
    await yy.eor(text)


@kasta_cmd(
    pattern="ud(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    word = await ga.get_text(kst)
    if not word:
        return await kst.eor("`Provide a word!`", time=5)
    yy = await kst.eor("`Processing...`")
    url = "http://api.urbandictionary.com/v0/define"
    res = await Fetch(
        url,
        params={"term": word},
        re_json=True,
    )
    if not res:
        return await yy.eod("`Try again now!`")
    try:
        res = res["list"][0]
    except IndexError:
        return await yy.eod(f"**No Results for:** `{word}`")
    text = "• **Given Word:** `{}`\n• **Meaning:** `{}`\n• **Example:** `{}`".format(
        res.get("word").strip(),
        res.get("definition").strip(),
        res.get("example").strip(),
    )
    await yy.eor(text)


@kasta_cmd(
    pattern="mean(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    word = await ga.get_text(kst)
    if not word:
        return await kst.eor("`Provide a word!`", time=5)
    yy = await kst.eor("`Processing...`")
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod(f"**No Results for:** `{word}`")
    defi = res[0]["meanings"][0]["definitions"][0]
    exa = defi["example"] if defi.get("example") else ""
    text = "• **Given Word:** `{}`\n• **Meaning:** `{}`\n• **Example:** `{}`".format(word, defi["definition"], exa)
    if defi.get("synonyms"):
        text += "\n• **Synonyms:**" + "".join(f" {x}," for x in defi["synonyms"])[:-1][:10]
    if defi.get("antonyms"):
        text += "\n**Antonyms:**" + "".join(f" {x}," for x in defi["antonyms"])[:-1][:10]
    await yy.eor(text)


@kasta_cmd(
    pattern="kbbi(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    word = await ga.get_text(kst)
    if not word:
        return await kst.eor("`Provide a word!`", time=5)
    yy = await kst.eor("`Processing...`")
    try:
        from kbbi import KBBI
    except ImportError:
        KBBI = import_lib(
            lib_name="kbbi",
            pkg_name="kbbi==0.4.3",
        ).KBBI
    try:
        mean = await aioify(KBBI, word)
    except BaseException:
        return await yy.eod(f"**No Results for:** `{word}`")
    text = f"• **Given Word:** `{word}`\n{mean}"
    await yy.eor(text)


@kasta_cmd(
    pattern="eod$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    now = datetime.now(TZ)
    month = now.strftime("%b")
    url = "https://daysoftheyear.com"
    url += f"/days/{month}/" + now.strftime("%F").split("-")[2]
    res = await Fetch(url, re_content=True)
    if not res:
        return await yy.eod("`Try again now!`")
    soup = BeautifulSoup(res, "html.parser", from_encoding="utf-8")
    days = soup.find_all("a", "js-link-target", href=re.compile(r"daysoftheyear.com/days"))
    text = "🎊 **Events of the Day**\n"
    for x in days[:5]:
        text += "• [{}]({})\n".format(x.text, x["href"])
    await yy.eor(text)


@kasta_cmd(
    pattern="lorem$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    url = "https://loripsum.net/api/plaintext"
    res = await Fetch(url)
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.eor(res.strip(), parts=True, parse_mode=parse_pre)


@kasta_cmd(
    pattern="wtr(s|p|)(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    mode = kst.pattern_match.group(1).strip()
    city = await ga.get_text(kst, group=2)
    yy = await kst.eor("`Processing...`")
    city = city.replace(" ", "%20")
    if mode == "p":
        url = f"https://wttr.in/{city}_2&lang=en.png"
    elif mode == "s":
        url = "https://wttr.in/" + (city + "?format=%l:+%c+%t,+%w+%m" if city else "?format=%l:+%c+%t,+%w+%m&lang=en")
    else:
        url = f"https://wttr.in/{city}?m?M?0?q?T&lang=en"
    res = await Fetch(url, re_content=mode == "p")
    if not res:
        return await yy.eod("`Try again now!`")
    if mode != "p":
        res = escape(res)
        await yy.eor(f"<pre>{res}</pre>", parse_mode="html")
    else:
        await yy.eor(
            file=res,
            force_document=False,
        )


@kasta_cmd(
    pattern="calc(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    text = await ga.get_text(kst)
    yy = await kst.eor("`Processing...`")
    if not text:
        return await kst.eor("`Provide a math!`", time=5)
    text = " ".join(text.split())
    newtext = replace_all(
        text.lower(),
        {
            ":": "/",
            "÷": "/",
            "×": "*",
            "x": "*",
        },
    )
    try:
        answer = f"{text} = {eval(newtext)}"
    except Exception as err:
        answer = f"{text} = {err}"
    await yy.eor(answer, parse_mode=parse_pre)


@kasta_cmd(
    pattern=r"haste(?: |$)([\s\S]*)",
)
async def _(kst):
    ga = kst.client
    text = await ga.get_text(kst)
    if not text:
        return await kst.eor("`Provide a text!`", time=5)
    yy = await kst.eor("`Processing...`")
    url = "https://hastebin.com"
    res = await Fetch(
        f"{url}/documents",
        post=True,
        data=text.encode("utf-8"),
        re_json=True,
    )
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.eor("{}/{}.txt".format(url, res.get("key")))


@kasta_cmd(
    pattern="github(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    username = await ga.get_text(kst)
    if not username:
        return await kst.eor("`Provide a username!`", time=5)
    yy = await kst.eor("`Processing...`")
    username = username.replace("@", "")
    url = f"https://api.github.com/users/{username}"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod(f"`No GitHub user {username}.`")
    gid = res.get("id")
    gavatar = f"https://avatars.githubusercontent.com/u/{gid}"
    text = """
<b><a href={}>GITHUB</a></b>
<b>Name</b>  –  <code>{}</code>
<b>Username</b>  –  <code>{}</code>
<b>ID</b>  –  <code>{}</code>
<b>Type</b>  –  <code>{}</code>
<b>Company</b>  –  <code>{}</code>
<b>Blog</b>  –  <code>{}</code>
<b>Location</b>  –  <code>{}</code>
<b>Bio</b>  –  <code>{}</code>
<b>Public Repos</b>  –  <code>{}</code>
<b>Public Gists</b>  –  <code>{}</code>
<b>Followers</b>  –  <code>{}</code>
<b>Following</b>  –  <code>{}</code>
<b>Profile Created</b>  –  <code>{}</code>
<b>Profile Updated</b>  –  <code>{}</code>
""".format(
        res.get("html_url"),
        res.get("name"),
        res.get("login"),
        gid,
        res.get("type"),
        res.get("company") or "?",
        res.get("blog") or "?",
        res.get("location") or "?",
        res.get("bio") or "?",
        res.get("public_repos"),
        res.get("public_gists"),
        res.get("followers"),
        res.get("following"),
        res.get("created_at"),
        res.get("updated_at"),
    )
    try:
        file = None
        avatar = await Fetch(gavatar, re_content=True)
        if avatar:
            file = Root / "downloads/avatar.jpeg"
            async with aiofiles.open(file, mode="wb") as f:
                await f.write(avatar)
            gavatar = file
        await yy.eor(
            text,
            file=gavatar,
            force_document=False,
            parse_mode="html",
        )
        if file:
            (file).unlink(missing_ok=True)
    except BaseException:
        await yy.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="tovn$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    reply = await kst.get_reply_message()
    if not reply.media:
        return await yy.eor("`Is not media message!`", time=5)
    mt = get_media_type(reply.media)
    if not mt.startswith(("audio", "video")):
        return await yy.eor("`Is not audio/video files!`", time=5)
    file = await reply.download_media(file="downloads")
    voice = "downloads/voice.opus"
    await Runner(f"ffmpeg -i {file} -map 0:a -codec:a libopus -b:a 100k -vbr on {voice}")
    (Root / file).unlink(missing_ok=True)
    try:
        await yy.eor(
            file=voice,
            force_document=False,
            voice_note=True,
        )
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")
    (Root / voice).unlink(missing_ok=True)


@kasta_cmd(
    pattern=r"tgh(?: |$)([\s\S]*)",
)
async def _(kst):
    ga = kst.client
    text = await ga.get_text(kst)
    if not text and not kst.is_reply:
        return await kst.eor("`Provide a text or reply!`", time=5)
    yy = await kst.eor("`Processing...`")
    reply = await kst.get_reply_message()
    if kst.is_reply and reply.media:
        res, file = await reply.download_media(file="downloads"), ""
        mt = get_media_type(reply.media)
        if mt == "sticker":
            file = "downloads/sticker.png"
            Image.open(res).save(file)
            (Root / res).unlink(missing_ok=True)
            res = file
        elif mt == "sticker_anim":
            file = "downloads/sticker.gif"
            await Runner(f"lottie_convert.py {res} {file}")
            (Root / res).unlink(missing_ok=True)
            res = file
        if mt not in {"document", "text"}:
            try:
                tg = await Telegraph()
                up = await tg.upload_file(res)
                link = "https://telegra.ph" + next((_ for _ in up), "")
                push = f"**Telegraph:** [Telegraph Link]({link})"
            except Exception as err:
                push = f"**ERROR:**\n`{err}`"
            (Root / res).unlink(missing_ok=True)
            if file:
                (Root / file).unlink(missing_ok=True)
            return await yy.eor(push)
        text = (Root / res).read_text()
        (Root / res).unlink(missing_ok=True)
    tg = await Telegraph(ga.full_name)
    if not tg:
        return await yy.eod("`Try again now!`")
    push = await tg.create_page(title=text[:256], content=[text])
    res = push.get("url")
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.eor(f"**Telegraph:** [Telegraph Link]({res})")


@kasta_cmd(
    pattern="gps(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    locco = await ga.get_text(kst)
    if not locco:
        return await kst.eor("`Provide a location or coordinates!`", time=5)
    yy = await kst.eor("`Finding...`")
    try:
        from geopy.geocoders import Nominatim
    except ImportError:
        Nominatim = import_lib(
            lib_name="geopy.geocoders",
            pkg_name="geopy==2.4.1",
        ).Nominatim
    geolocator = Nominatim(user_agent="getter")
    location = geolocator.geocode(locco)
    if location:
        lat = location.latitude
        lon = location.longitude
        addr = location.address
        details = f"**Location:** `{locco}`\n**Address:** `{addr}`\n**Coordinates:** `{lat},{lon}`"
        return await yy.eor(
            details,
            file=typ.InputMediaGeoPoint(typ.InputGeoPoint(lat, lon)),
            force_document=True,
        )
    await yy.eod(f"**No Location found:** `{locco}`")


@kasta_cmd(
    pattern="getmsg( -s|silent|)(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    link = await ga.get_text(kst, group=2)
    if not link and not kst.is_reply:
        return await kst.eor("`Provide a message link or reply media!`", time=5)
    is_silent = any(_ in kst.pattern_match.group(1) for _ in ("-s", "silent"))
    if is_silent:
        await kst.try_delete()
    else:
        yy = await kst.eor("`Processing...`")
    reply = await kst.get_reply_message()
    if (kst.is_reply and not reply.message) or getattr(reply, "media", None):
        link = reply.msg_link
    if link.endswith("?single"):
        link = link.replace("?single", "")
    chat, msg_id = get_msg_id(link)
    if not is_silent and not (chat and msg_id):
        return await yy.eor(
            "Provide a valid message link!\n**E.g:** `https://t.me/tldevs/11` or `https://t.me/tldevs/19`"
        )
    try:
        from_msg = await ga.get_messages(chat, ids=msg_id)
    except Exception as err:
        if not is_silent:
            await yy.eor(formatx_send(err), parse_mode="html")
        return
    if not is_silent and not from_msg.media:
        await yy.try_delete()
    else:
        if not is_silent:
            await yy.eor("`Downloading...`")
        if isinstance(from_msg.media, typ.MessageMediaPhoto):
            file = "getmsg_" + str(msg_id) + ".jpg"
        else:
            mimetype = from_msg.media.document.mime_type
            file = "getmsg_" + str(msg_id) + guess_extension(mimetype)
        await ga.download_file(from_msg.media, file=file)
        msg = await yy.eor(
            f"**Source:** `{link}`",
            file=file,
            force_document=True,
        )
        await sendlog(msg, forward=True)
        if is_silent:
            await msg.try_delete()
        (Root / file).unlink(missing_ok=True)


@kasta_cmd(
    pattern="search( -r|revert|)(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    args = await ga.get_text(kst, group=2)
    if not args or len(args) < 2:
        return await kst.eor("`Provide a text to search!`", time=5)
    yy = await kst.eor("`Searching...`")
    limit = 5
    if ":" in args:
        args, limit = args.split(":", 1)
    try:
        limit = int(limit)
    except BaseException:
        pass
    limit = 99 if limit > 99 else limit  # noqa
    current, result, total = normalize_chat_id(kst.chat_id), "", 0
    async for msg in ga.iter_messages(
        current,
        search=args.strip(),
        limit=limit,
        reverse=bool(kst.pattern_match.group(1).strip()),
    ):
        result += f"• [{msg.id}](https://t.me/c/{current}/{msg.id})\n"
        total += 1
    text = f"**Search Results for:** `{args}`\n{result}" if total > 0 else f"**No Results for:** `{args}`"
    await yy.eor(text)


plugins_help["utility"] = {
    "{i}spcheck [text]/[reply]": "Check spelling of the text/sentence.",
    "{i}ud [word]/[reply]": "Fetch the word defenition from urbandictionary.",
    "{i}mean [word]/[reply]": "Get the meaning of the word.",
    "{i}kbbi [word]/[reply]": "Get the meaning of the word/phrase with KBBI Daring.",
    "{i}eod": "Get event of the today.",
    "{i}lorem": "Get lorem ipsum.",
    "{i}wtr [city]/[reply]": "Get ASCII-Art of current weather by city.",
    "{i}wtrs [city]/[reply]": "Get a simple weather.",
    "{i}wtrp [city]/[reply]": "Get a weather pictures.",
    "{i}calc [math]/[reply]": "Simpler calculator supported ( : ÷ × x ). E.g: 2 x 2",
    "{i}haste [text]/[reply]": "Upload text to hastebin.",
    "{i}github [username]/[reply]": "Get full information about an user on GitHub of given username.",
    "{i}tovn [reply]": "Convert replied audio/video file to voice note.",
    "{i}tgh [text]/[reply]": "Upload text or media to Telegraph.",
    "{i}gps [location/coordinates]/[reply]": "Send the map a given location.",
    "{i}getmsg [-s/silent] [link]/[reply]": "Get any media from messages forward/copy restrictions or replied message.",
    "{i}search [-r/revert] [text]/[reply] : [number]": "Search messages in current chat. Add '-r' to reverse order. Limit number of result is 99.",
}
