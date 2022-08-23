# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from random import randrange
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    UserStatusEmpty,
    UserStatusLastMonth,
)
from . import (
    kasta_cmd,
    plugins_help,
    choice,
    shorten,
    suppress,
    mentionuser,
    display_name,
    get_user,
    EMOJITAG,
)

ATAGS = []
ETAGS = []
DEFAULT_PERUSER = 6
DEFAULT_SEP = "|"


@kasta_cmd(
    pattern="all$|@all$",
    no_crash=True,
    groups_only=True,
)
async def _(kst):
    tag = "\U000e0020all"
    msg = f"@{tag}"
    slots = 4096 - len(msg)
    chat = await kst.get_input_chat()
    async for x in kst.client.iter_participants(chat):
        if exclude_user(x):
            msg += mentionuser(x.id, "\u2063")
            slots -= 1
            if slots == 0:
                break
    await kst.respond(msg, reply_to=kst.reply_to_msg_id)
    await kst.try_delete()


@kasta_cmd(
    pattern=r"atag(?: |$)([\s\S]*)",
    no_crash=True,
    groups_only=True,
)
async def _(kst):
    chat_id = kst.chat_id
    if chat_id in ATAGS:
        await kst.eor("`Please wait until previous ATAG finished...`", time=5, silent=True)
        return
    caption = kst.pattern_match.group(1)
    users = []
    limit = 0
    ATAGS.append(chat_id)
    msg = await kst.sod("`In atag process...`", delete=False, force_reply=True)
    chat = await kst.get_input_chat()
    admins = await kst.client.get_participants(chat, filter=ChannelParticipantsAdmins)
    admins_id = [x.id for x in admins]
    async for x in kst.client.iter_participants(chat):
        if exclude_user(x):
            if x.id not in admins_id:
                users.append(to_mention(x))
            if isinstance(x.participant, ChannelParticipantAdmin):
                users.append("<b>👮 Admin:</b> {}".format(to_mention(x)))
            if isinstance(x.participant, ChannelParticipantCreator):
                users.append("<b>🤴 Owner:</b> {}".format(to_mention(x)))
    caption = f"{caption}\n" if caption else caption
    for men in list(user_list(users, DEFAULT_PERUSER)):
        try:
            if chat_id not in ATAGS:
                await kst.try_delete()
                await msg.try_delete()
                return
            await kst.respond(
                caption + "  {}  ".format(DEFAULT_SEP).join(map(str, men)),
                reply_to=kst.reply_to_msg_id,
                parse_mode="html",
            )
            limit += DEFAULT_PERUSER
            await asyncio.sleep(randrange(5, 7))
        except BaseException:
            pass
    with suppress(ValueError):
        ATAGS.remove(chat_id)
    await kst.try_delete()
    await msg.try_delete()


@kasta_cmd(
    pattern="acancel$",
    no_crash=True,
    groups_only=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if kst.chat_id not in ATAGS:
        await msg.eod("__No current atag are running.__")
        return
    with suppress(ValueError):
        ATAGS.remove(kst.chat_id)
    await msg.eor("`cancelled`", time=5)


@kasta_cmd(
    pattern=r"etag(?: |$)([\s\S]*)",
    no_crash=True,
    groups_only=True,
)
async def _(kst):
    chat_id = kst.chat_id
    if chat_id in ETAGS:
        await kst.eor("`Please wait until previous ETAG finished...`", time=5, silent=True)
        return
    caption = kst.pattern_match.group(1)
    users = []
    limit = 0
    ETAGS.append(chat_id)
    msg = await kst.sod("`In etag process...`", delete=False, force_reply=True)
    chat = await kst.get_input_chat()
    admins = await kst.client.get_participants(chat, filter=ChannelParticipantsAdmins)
    admins_id = [x.id for x in admins]
    async for x in kst.client.iter_participants(chat):
        if exclude_user(x):
            if x.id not in admins_id:
                users.append(" {} ".format(mentionuser(x.id, choice(EMOJITAG), html=True)))
            if isinstance(x.participant, ChannelParticipantAdmin):
                users.append(" {} ".format(mentionuser(x.id, choice(EMOJITAG), html=True)))
            if isinstance(x.participant, ChannelParticipantCreator):
                users.append(" {} ".format(mentionuser(x.id, choice(EMOJITAG), html=True)))
    caption = f"{caption}\n" if caption else caption
    for men in list(user_list(users, DEFAULT_PERUSER)):
        try:
            if chat_id not in ETAGS:
                await kst.try_delete()
                await msg.try_delete()
                return
            await kst.respond(
                caption + " ".join(map(str, men)),
                reply_to=kst.reply_to_msg_id,
                parse_mode="html",
            )
            limit += DEFAULT_PERUSER
            await asyncio.sleep(randrange(5, 7))
        except BaseException:
            pass
    with suppress(ValueError):
        ETAGS.remove(chat_id)
    await kst.try_delete()
    await msg.try_delete()


@kasta_cmd(
    pattern="ecancel$",
    no_crash=True,
    groups_only=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if kst.chat_id not in ETAGS:
        await msg.eod("__No current etag are running.__")
        return
    with suppress(ValueError):
        ETAGS.remove(kst.chat_id)
    await msg.eor("`cancelled`", time=5)


@kasta_cmd(
    pattern="report$",
    no_crash=True,
    groups_only=True,
    func=lambda e: e.is_reply,
)
async def _(kst):
    tag = "\U000e0020admin"
    msg = f"@{tag}"
    chat = await kst.get_input_chat()
    async for x in kst.client.iter_participants(chat, filter=ChannelParticipantsAdmins):
        if exclude_user(x):
            msg += mentionuser(x.id, "\u2063")
    await kst.respond(msg, reply_to=kst.reply_to_msg_id)
    await kst.try_delete()


@kasta_cmd(
    pattern=r"(mention|men)(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    user, name = await get_user(kst, 2)
    if not user:
        return
    name = name if name else "ㅤ"
    mention = f"<a href=tg://user?id={user.id}>{name}</a>"
    await kst.sod(mention, parse_mode="html")


def to_mention(user) -> str:
    return mentionuser(user.id, shorten(display_name(user), width=20, placeholder="..."), html=True)


def exclude_user(x) -> bool:
    return (
        True
        if not (
            x.deleted
            or x.bot
            or x.is_self
            or (hasattr(x.participant, "admin_rights") and x.participant.admin_rights.anonymous)
        )
        and not isinstance(x.status, (UserStatusLastMonth, UserStatusEmpty))
        else False
    )


def user_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i : i + n]


plugins_help["mention"] = {
    "{i}all|@all": "Mention the lucky members in current group.",
    "{i}atag [or reply] [caption (optional)]": "Mention all members in current group.",
    "{i}acancel": "Stop the current process of {i}atag.",
    "{i}etag [or reply] [caption (optional)]": "Mention all members in current group with random emoji.",
    "{i}ecancel": "Stop the current process of {i}etag.",
    "{i}report [reply]": "Report reply messages to admin.",
    "{i}mention|{i}men [reply/username] [text]": "Tags that person with the given custom text.",
}
