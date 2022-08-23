# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import mimetypes
import sys
import time
import aiohttp
from geopy.geocoders import Nominatim
from telethon.tl.types import MessageMediaPhoto, InputMediaGeoPoint, InputGeoPoint
from . import (
    __version__,
    Root,
    kasta_cmd,
    plugins_help,
    suppress,
    is_url,
    time_formatter,
    get_random_hex,
    get_chat_msg_id,
    Searcher,
)


@kasta_cmd(
    pattern="getmsg(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    link = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(1)
    if not link:
        await kst.eor("`Provide a message link!`", time=5)
        return
    msg = await kst.eor("`Processing...`")
    chat, msg_id = get_chat_msg_id(link)
    if not (chat and msg_id):
        await msg.eor("Provide a valid message link!\n**Eg:** `https://t.me/tldevs/11` or `https://t.me/tldevs/19`")
        return
    start_time = time.time()
    try:
        from_msg = await kst.client.get_messages(chat, ids=msg_id)
    except Exception as err:
        await kst.eor(f"**ERROR**\n`{err}`")
    if not from_msg.media:
        await msg.try_delete()
    else:
        await msg.eor("`Downloading...`")
        if isinstance(from_msg.media, MessageMediaPhoto):
            file = "getmsg_" + get_random_hex() + ".jpg"
        else:
            mimetype = from_msg.media.document.mime_type
            file = "getmsg_" + get_random_hex() + mimetypes.guess_extension(mimetype)
        with suppress(BaseException):
            await kst.client.download_file(from_msg.media, file=file)
            taken = time_formatter((time.time() - start_time) * 1000)
            await msg.eor("`Uploading...`")
            caption = rf"""\\**#Getter**//
**Up:** `{file}`
**Source:** `{link}`
**Taken:** `{taken}`"""
            await kst.client.send_file(
                kst.chat_id,
                file=file,
                caption=caption,
                force_document=True,
                allow_cache=False,
                reply_to=kst.reply_to_msg_id,
                silent=True,
            )
        await msg.try_delete()
        (Root / file).unlink(missing_ok=True)


@kasta_cmd(
    pattern="gps(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    place = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(1)
    if not place:
        await kst.eor("`Provide a place!`", time=5)
        return
    msg = await kst.eor("`Finding...`")
    geolocator = Nominatim(user_agent="getter")
    place = place.replace("\n", " ").strip()
    geoloc = geolocator.geocode(place)
    if geoloc:
        lon = geoloc.longitude
        lat = geoloc.latitude
        with suppress(BaseException):
            caption = f"**Location:** `{place}`"
            await kst.client.send_file(
                kst.chat_id,
                file=InputMediaGeoPoint(InputGeoPoint(lat, lon)),
                caption=caption,
                force_document=True,
                reply_to=kst.reply_to_msg_id or None,
                silent=True,
            )
        await msg.try_delete()
        return
    await msg.eor("`I coudn't find it.`", time=5)


@kasta_cmd(
    pattern="(google|duck|yandex|bing|yahoo|baidu|ecosia)(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    engine = kst.pattern_match.group(1)
    keywords = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(2)
    if not keywords:
        await kst.eor("`Provide a keywords!`", time=5)
        return
    msg = await kst.eor("`Searching...`")
    if engine == "google":
        search = "Google"
        url = "https://www.google.com/search?q={}"
    elif engine == "duck":
        search = "DuckDuckGo"
        url = "https://duckduckgo.com/?q={}&kp=-2&kac=1"
    elif engine == "yandex":
        search = "Yandex"
        url = "https://yandex.com/search/?text={}"
    elif engine == "bing":
        search = "Bing"
        url = "https://www.bing.com/search?q={}"
    elif engine == "yahoo":
        search = "Yahoo"
        url = "https://search.yahoo.com/search?p={}"
    elif engine == "baidu":
        search = "Baidu"
        url = "https://www.baidu.com/s?wd={}"
    elif engine == "ecosia":
        search = "Ecosia"
        url = "https://www.ecosia.org/search?q={}"
    result = url.format(keywords.replace("\n", " ").replace(" ", "+")).strip()
    keywords = keywords.replace("\n", " ").strip()
    await msg.eor("**🔎 {} Search Result:**\n[{}]({})".format(search, keywords, result))


@kasta_cmd(
    pattern="(un|)short(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    text = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(2)
    if not text or is_url(text) is not True:
        await kst.eor("`Provide a valid link!`", time=5)
        return
    msg = await kst.eor("`Processing...`")
    headers = {
        "User-Agent": "Python/{0[0]}.{0[1]} aiohttp/{1} getter/{2}".format(
            sys.version_info,
            aiohttp.__version__,
            __version__,
        )
    }
    if kst.pattern_match.group(1).strip() == "un":
        res = await Searcher(
            url=text,
            headers=headers,
            real=True,
            allow_redirects=False,
        )
        if not res:
            return await msg.eod("`Try again now!`")
        output = "**Unshorted Link:** {}\n**Your Link:** {}".format(res.headers.get("location"), text)
    else:
        url = f"https://da.gd/s?url={text}"
        res = await Searcher(
            url=url,
            headers=headers,
        )
        if not res:
            return await msg.eod("`Try again now!`")
        output = "**Shorted Link:** {}\n**Your Link:** {}".format(res.strip(), text)
    await msg.eor(output)


plugins_help["utility"] = {
    "{i}getmsg [link/reply]": "Get media from messages forward/copy restrictions.",
    "{i}gps [place/reply]": "To send the map of the given location.",
    "{i}google [keywords/reply]": "How to Google...",
    "{i}duck [keywords/reply]": "How to DuckDuckGo...",
    "{i}yandex [keywords/reply]": "How to Yandex...",
    "{i}bing [keywords/reply]": "How to Bing...",
    "{i}yahoo [keywords/reply]": "How to Yahoo...",
    "{i}baidu [keywords/reply]": "How to Baidu...",
    "{i}ecosia [keywords/reply]": "How to Ecosia...",
    "{i}short [link/reply]": "Shorten a link into `da.gd` link.",
    "{i}unshort [shortlink/reply]": "Reverse the shortened link to real link.",
}
