# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from telethon.errors import YouBlockedUserError
from telethon.events import NewMessage
from telethon.tl.functions.contacts import UnblockRequest
from . import kasta_cmd, plugins_help, suppress

TW_BOT = "tweedlbot"
TT_BOT = "downloader_tiktok_bot"


@kasta_cmd(
    pattern="tw(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    link = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(1)
    if not link:
        await kst.eor("`Provide a valid tweet link!`", time=5)
        return
    msg = await kst.eor("`Downloading...`")
    resp = None
    async with kst.client.conversation(TW_BOT) as conv:
        resp = await conv_tw(conv, link)
    if not resp:
        return await msg.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "document", None):
        return await msg.eod(f"`{resp.message.message}`")
    file = resp.message.media
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            force_document=False,
            caption=f"**Link:** `{link}`",
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    with suppress(BaseException):
        await kst.client.delete_dialog(TW_BOT, revoke=True)
    await kst.try_delete()


@kasta_cmd(
    pattern="tt(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    link = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(1)
    if not link:
        await kst.eor("`Provide a valid tiktok link!`", time=5)
        return
    msg = await kst.eor("`Downloading...`")
    resp = None
    async with kst.client.conversation(TT_BOT) as conv:
        resp = await conv_tt(conv, link)
    if not resp:
        return await msg.eod("`Bot did not respond.`")
    if not getattr(resp.message.media, "document", None):
        return await msg.eod(f"`{resp.message.message}`")
    file = resp.message.media
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            force_document=False,
            caption=f"**Link:** `{link}`",
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    with suppress(BaseException):
        await kst.client.delete_dialog(TT_BOT, revoke=True)
    await kst.try_delete()


async def conv_tt(conv, link):
    try:
        resp = conv.wait_event(NewMessage(incoming=True, from_users=conv.chat_id))
        await conv.send_message(link)
        resp = await resp
        await resp.mark_read(clear_mentions=True)
        return resp
    except YouBlockedUserError:
        await conv._client(UnblockRequest(conv.chat_id))
        return await conv_tt(conv, link)


async def conv_tw(conv, link):
    try:
        resp = conv.wait_event(NewMessage(incoming=True, from_users=conv.chat_id))
        await conv.send_message(link)
        resp = await resp
        await resp.mark_read(clear_mentions=True)
        return resp
    except YouBlockedUserError:
        await conv._client(UnblockRequest(conv.chat_id))
        return await conv_tw(conv, link)


plugins_help["downloader"] = {
    "{i}tw [link/reply]": "Download high quality of video from Twitter.",
    "{i}tt [link/reply]": "Download video from TikTok without watermark.",
}
