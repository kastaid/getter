# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio

from telethon import events
from telethon.errors import YouBlockedUserError

from . import kasta_cmd, plugins_help

TW_BOT = "tweedlbot"
TT_BOT = "downloader_tiktok_bot"


@kasta_cmd(
    pattern="tw(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    link = await ga.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid tweet link!`", time=5)
    yy = await kst.eor("`Downloading...`")
    async with ga.conversation(TW_BOT) as conv:
        resp = await conv_tw(conv, link)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "document", None):
        return await yy.eod(f"`{resp.message.message}`")
    file = resp.message.media
    await yy.eor(
        f"**Link:** `{link}`",
        file=file,
        force_document=False,
    )
    await ga.delete_chat(TW_BOT, revoke=True)


@kasta_cmd(
    pattern="tt(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    link = await ga.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid tiktok link!`", time=5)
    yy = await kst.eor("`Downloading...`")
    async with ga.conversation(TT_BOT) as conv:
        resp = await conv_tt(conv, link)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "document", None):
        return await yy.eod(f"`{resp.message.message}`")
    file = resp.message.media
    await yy.eor(
        f"**Link:** `{link}`",
        file=file,
        force_document=False,
    )
    await ga.delete_chat(TT_BOT, revoke=True)


async def conv_tt(conv, link):
    try:
        resp = conv.wait_event(
            events.NewMessage(
                incoming=True,
                from_users=conv.chat_id,
            ),
        )
        await conv.send_message(link)
        resp = await resp
        await resp.read(
            clear_mentions=True,
            clear_reactions=True,
        )
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_tt(conv, link)


async def conv_tw(conv, link):
    try:
        resp = conv.wait_event(
            events.NewMessage(
                incoming=True,
                from_users=conv.chat_id,
            ),
        )
        await conv.send_message(link)
        resp = await resp
        await resp.read(
            clear_mentions=True,
            clear_reactions=True,
        )
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
