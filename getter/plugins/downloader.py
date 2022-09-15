# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from telethon.errors.rpcerrorlist import YouBlockedUserError
from . import (
    kasta_cmd,
    plugins_help,
    events,
    suppress,
)

TW_BOT = "tweedlbot"
TT_BOT = "downloader_tiktok_bot"


@kasta_cmd(
    pattern="tw(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    link = await ga.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid tweet link!`", time=5)
        return
    yy = await kst.eor("`Downloading...`")
    async with ga.conversation(TW_BOT) as conv:
        resp = await conv_tw(conv, link)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "document", None):
        return await yy.eod(f"`{resp.message.message}`")
    file = resp.message.media
    with suppress(BaseException):
        await kst.respond(
            f"**Link:** `{link}`",
            file=file,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await ga.delete_chat(TW_BOT, revoke=True)
    await yy.try_delete()


@kasta_cmd(
    pattern="tt(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    link = await ga.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid tiktok link!`", time=5)
        return
    yy = await kst.eor("`Downloading...`")
    async with ga.conversation(TT_BOT) as conv:
        resp = await conv_tt(conv, link)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "document", None):
        return await yy.eod(f"`{resp.message.message}`")
    file = resp.message.media
    with suppress(BaseException):
        await kst.respond(
            f"**Link:** `{link}`",
            file=file,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await ga.delete_chat(TT_BOT, revoke=True)
    await yy.try_delete()


async def conv_tt(conv, link):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        await conv.send_message(link)
        resp = await resp
        await resp.mark_read(clear_mentions=True)
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_tt(conv, link)


async def conv_tw(conv, link):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        await conv.send_message(link)
        resp = await resp
        await resp.mark_read(clear_mentions=True)
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_tw(conv, link)


plugins_help["downloader"] = {
    "{i}tw [link]/[reply]": "Download high quality of video from Twitter.",
    "{i}tt [link]/[reply]": "Download video from TikTok without watermark.",
}
