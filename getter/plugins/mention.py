# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from random import randrange
from telethon.tl import types as typ
from . import (
    kasta_cmd,
    plugins_help,
    choice,
    mentionuser,
    display_name,
    get_user_status,
    get_user,
    normalize_chat_id,
    md_to_html,
    chunk,
    EMOJI_TAGS,
)

ATAGS = []
ETAGS = []
DEFAULT_PERUSER = 6
DEFAULT_SEP = "|"


@kasta_cmd(
    pattern="all$|@all$",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    tag = "\U000e0020all"
    yy = f"@{tag}"
    slots = 4096 - len(yy)
    async for x in ga.iter_participants(chat_id):
        if exclude_user(x):
            yy += mentionuser(x.id, "\u2063")
            slots -= 1
            if slots == 0:
                break
    await kst.respond(yy, reply_to=kst.reply_to_msg_id)
    await kst.try_delete()


@kasta_cmd(
    pattern=r"atag(?: |$)([\s\S]*)",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    if chat_id in ATAGS:
        await kst.eor("`Please wait until previous • atag • finished...`", time=5, silent=True)
        return
    caption = kst.pattern_match.group(1)
    users, limit = [], 0
    ATAGS.append(chat_id)
    yy = await kst.sod("`In atag process...`", delete=False, force_reply=True)
    async for x in ga.iter_participants(chat_id):
        if exclude_user(x):
            if not hasattr(x.participant, "admin_rights"):
                users.append(mentionuser(x.id, display_name(x), html=True))
            if isinstance(x.participant, typ.ChannelParticipantAdmin):
                users.append("👮 {}".format(mentionuser(x.id, display_name(x), html=True)))
            if isinstance(x.participant, typ.ChannelParticipantCreator):
                users.append("🤴 {}".format(mentionuser(x.id, display_name(x), html=True)))
    caption = f"{md_to_html(caption)}\n" if caption else caption
    for men in chunk(users, DEFAULT_PERUSER):
        try:
            if chat_id not in ATAGS:
                break
            await kst.respond(
                caption + "  {}  ".format(DEFAULT_SEP).join(map(str, men)),
                reply_to=kst.reply_to_msg_id,
                parse_mode="html",
            )
            limit += DEFAULT_PERUSER
            await asyncio.sleep(randrange(5, 7))
        except BaseException:
            pass
    if chat_id in ATAGS:
        ATAGS.remove(chat_id)
    await yy.try_delete()


@kasta_cmd(
    pattern=r"etag(?: |$)([\s\S]*)",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    if chat_id in ETAGS:
        await kst.eor("`Please wait until previous • etag • finished...`", time=5, silent=True)
        return
    caption = kst.pattern_match.group(1)
    users, limit = [], 0
    ETAGS.append(chat_id)
    yy = await kst.sod("`In etag process...`", delete=False, force_reply=True)
    async for x in ga.iter_participants(chat_id):
        if exclude_user(x):
            if not hasattr(x.participant, "admin_rights"):
                users.append(mentionuser(x.id, choice(EMOJI_TAGS), html=True))
            if isinstance(x.participant, typ.ChannelParticipantAdmin):
                users.append("👮 {}".format(mentionuser(x.id, choice(EMOJI_TAGS), html=True)))
            if isinstance(x.participant, typ.ChannelParticipantCreator):
                users.append("🤴 {}".format(mentionuser(x.id, choice(EMOJI_TAGS), html=True)))
    caption = f"{md_to_html(caption)}\n" if caption else caption
    for men in chunk(users, DEFAULT_PERUSER):
        try:
            if chat_id not in ETAGS:
                break
            await kst.respond(
                caption + " ".join(map(str, men)),
                reply_to=kst.reply_to_msg_id,
                parse_mode="html",
            )
            limit += DEFAULT_PERUSER
            await asyncio.sleep(randrange(5, 7))
        except BaseException:
            pass
    if chat_id in ETAGS:
        ETAGS.remove(chat_id)
    await yy.try_delete()


@kasta_cmd(
    pattern="(a|e)cancel$",
    groups_only=True,
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    match = kst.pattern_match.group(1)
    yy = await kst.eor("`Processing...`")
    if match == "a":
        if chat_id not in ATAGS:
            await yy.eod("__No current atag are running.__")
            return
        else:
            ATAGS.remove(chat_id)
    else:
        if chat_id not in ETAGS:
            await yy.eod("__No current etag are running.__")
            return
        else:
            ETAGS.remove(chat_id)
    await yy.eor("`cancelled`", time=5)


@kasta_cmd(
    pattern="report$",
    groups_only=True,
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    tag = "\U000e0020admin"
    yy = f"@{tag}"
    async for x in ga.iter_participants(chat_id, filter=typ.ChannelParticipantsAdmins):
        if exclude_user(x):
            yy += mentionuser(x.id, "\u2063")
    await kst.respond(yy, reply_to=kst.reply_to_msg_id)
    await kst.try_delete()


@kasta_cmd(
    pattern=r"(mention|men)(?: |$)([\s\S]*)",
)
async def _(kst):
    user, name = await get_user(kst, 2)
    if not user:
        return await kst.try_delete()
    name = name or display_name(user)
    mention = mentionuser(user.id, name, html=True, width=70)
    await kst.sod(mention, parse_mode="html")


def exclude_user(x) -> bool:
    return bool(
        not (
            x.deleted
            or x.bot
            or x.is_self
            or (hasattr(x.participant, "admin_rights") and x.participant.admin_rights.anonymous)
        )
        and get_user_status(x) != "long_time_ago"
    )


plugins_help["mention"] = {
    "{i}all|@all": "Mention the lucky members in current group.",
    "{i}atag [or reply] [caption]": "Mention all members in current group.",
    "{i}acancel": "Stop the current process of {i}atag.",
    "{i}etag [or reply] [caption]": "Mention all members in current group with random emoji.",
    "{i}ecancel": "Stop the current process of {i}etag.",
    "{i}report [reply]": "Report reply messages to admin.",
    "{i}mention|{i}men [reply]/[username/mention/id] [text]": "Tags that person with the given custom text.",
}