# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
import html
import math
import time
from cache import AsyncTTL
from cachetools import TTLCache
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.custom import Dialog
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.contacts import GetBlockedRequest, UnblockRequest
from telethon.tl.functions.messages import (
    GetAllStickersRequest,
    GetSavedGifsRequest,
    GetFullChatRequest,
    GetHistoryRequest,
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    Channel,
    Chat,
    User,
    ChatPhotoEmpty,
    ChannelParticipantsAdmins,
)
from . import (
    HELP,
    display_name,
    humanbool,
    get_user_status,
    get_user,
    kasta_cmd,
    parse_pre,
    Searcher,
)

ROSE_LANG_CACHE = TTLCache(maxsize=512, ttl=(120 * 30), timer=time.perf_counter)  # 1 hours
ROSE_STAT_CACHE = TTLCache(maxsize=512, ttl=120, timer=time.perf_counter)  # 2 mins
SPAMWATCH_CACHE = TTLCache(maxsize=512, ttl=120, timer=time.perf_counter)  # 2 mins
CAS_CACHE = TTLCache(maxsize=512, ttl=120, timer=time.perf_counter)  # 2 mins


@kasta_cmd(
    pattern="sg(?: |$)(.*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Checking...`")
    user, _ = await get_user(kst, 1)
    if not user:
        await msg.eor("`Required Username/ID or reply message.`", time=15)
        return
    sangmata = "@SangMataInfo_bot"
    resp = None
    async with kst.client.conversation(sangmata) as conv:
        try:
            await conv.send_message(f"/search_id {user.id}")
        except YouBlockedUserError:
            await kst.client(UnblockRequest(sangmata))
            await conv.send_message(f"/search_id {user.id}")
        text = []
        while True:
            try:
                resp = await conv.get_response(timeout=2)
            except asyncio.exceptions.TimeoutError:
                break
            text.append(resp.message)
        if resp:
            await resp.mark_read(clear_mentions=True)
            # await kst.client(telethon.tl.functions.messages.DeleteHistoryRequest(conv.chat_id, max_id=0, just_clear=False, revoke=True))
    if not text:
        return await msg.eod("`Sangmata did not respond.`")
    if len(text) == 1 and bool([x for x in text if x.startswith("🔗")]):
        return await msg.eod("`Can't get any records.`")
    if "No records found" in text:
        return await msg.eod("`Doesn't have any record.`")
    names, usernames = await sglist(text)
    if names:
        for x in names:
            if x.startswith("⚠️"):
                break
            await msg.sod(
                x,
                force_reply=True,
                parse_mode=parse_pre,
            )
    if usernames:
        for x in usernames:
            if x.startswith("⚠️"):
                break
            await msg.sod(
                x,
                force_reply=True,
                parse_mode=parse_pre,
            )


@kasta_cmd(
    pattern="created(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Checking...`")
    user, _ = await get_user(kst, 1)
    if user:
        user_id = user.id
    else:
        user_id = kst.client.uid
    created = "@creationdatebot"
    resp = None
    async with kst.client.conversation(created) as conv:
        try:
            await conv.send_message(f"/id {user_id}")
        except YouBlockedUserError:
            await kst.client(UnblockRequest(created))
            await conv.send_message(f"/id {user_id}")
        text = ""
        while True:
            try:
                resp = await conv.get_response(timeout=2)
            except asyncio.exceptions.TimeoutError:
                break
            text += resp.message
        if resp:
            await resp.mark_read(clear_mentions=True)
    if not text:
        return await msg.eod("`Bot did not respond.`")
    await msg.eor(text, parse_mode=parse_pre)


@kasta_cmd(
    pattern="total(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    if match:
        from_user = match
    elif kst.is_reply:
        from_user = (await kst.get_reply_message()).sender_id
    else:
        from_user = "me"
    msg = await kst.client.get_messages(kst.chat_id, limit=0, from_user=from_user)
    user = await kst.client.get_entity(from_user)
    await kst.eor(f"Total messages of <code>{display_name(user)}</code> [<code>{msg.total}</code>]", parse_mode="html")


@kasta_cmd(
    pattern="stats$",
)
async def _(kst):
    msg = await kst.eor("`Collecting stats...`")
    start_time = time.time()
    private_chats = 0
    bots = 0
    groups = 0
    broadcast_channels = 0
    admin_in_groups = 0
    creator_in_groups = 0
    admin_in_broadcast_channels = 0
    creator_in_channels = 0
    unread_mentions = 0
    unread = 0
    dialog: Dialog
    async for dialog in kst.client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.broadcast:
            broadcast_channels += 1
            if entity.creator or entity.admin_rights:
                admin_in_broadcast_channels += 1
            if entity.creator:
                creator_in_channels += 1
        elif (isinstance(entity, Channel) and entity.megagroup) or isinstance(entity, Chat):
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_in_groups += 1
            if entity.creator:
                creator_in_groups += 1
        elif isinstance(entity, User):
            private_chats += 1
            if entity.bot:
                bots += 1
        unread_mentions += dialog.unread_mentions_count
        unread += dialog.unread_count
    stop_time = time.time() - start_time
    try:
        ct = (await kst.client(GetBlockedRequest(1, 0))).count
    except AttributeError:
        ct = 0
    try:
        gs = await kst.client(GetSavedGifsRequest(0))
        gs_count = len(gs.gifs)
    except BaseException:
        gs_count = 0
    try:
        sp = await kst.client(GetAllStickersRequest(0))
        sp_count = len(sp.sets)
    except BaseException:
        sp_count = 0
    sc_count = await get_total_created(kst, "@Stickers", "/stats")
    bc_count = await get_total_created(kst, "@BotFather", "/setcommands")
    me = await kst.client.get_me()
    graph = f"<b>Stats for {display_name(me)}</b>"
    graph += f"\n ├ <b>Private:</b> <code>{private_chats}</code>\n"
    graph += f" ┊   ├ <b>Users:</b> <code>{private_chats - bots}</code>\n"
    graph += f" ┊   ├ <b>Bots:</b> <code>{bots}</code>\n"
    graph += f" ├ <b>Groups:</b> <code>{groups}</code>\n"
    graph += f" ├ <b>Channels:</b> <code>{broadcast_channels}</code>\n"
    graph += f" ├ <b>Admin Groups:</b> <code>{admin_in_groups}</code>\n"
    graph += f" ┊   ├ <b>Creator:</b> <code>{creator_in_groups}</code>\n"
    graph += f" ┊   ├ <b>Admin Rights:</b> <code>{admin_in_groups - creator_in_groups}</code>\n"
    graph += f" ├ <b>Admin Channels:</b> <code>{admin_in_broadcast_channels}</code>\n"
    graph += f" ┊   ├ <b>Creator:</b> <code>{creator_in_channels}</code>\n"
    graph += f" ┊   ├ <b>Admin Rights:</b> <code>{admin_in_broadcast_channels - creator_in_channels}</code>\n"
    graph += f" ├ <b>Unread:</b> <code>{unread}</code>\n"
    graph += f" ├ <b>Unread Mentions:</b> <code>{unread_mentions}</code>\n"
    graph += f" ├ <b>Blocked Users:</b> <code>{ct}</code>\n"
    graph += f" ├ <b>Gifs Saved:</b> <code>{gs_count}</code>\n"
    graph += f" ├ <b>Stickers Pack Installed:</b> <code>{sp_count}</code>\n"
    graph += f" ├ <b>Stickers Pack Created:</b> <code>{sc_count}</code>\n"
    graph += f" ├ <b>Bots Created:</b> <code>{bc_count}</code>\n"
    graph += f" └ <b>It Took:</b> <code>{stop_time:.02f}s</code>"
    await msg.eor(graph, parse_mode="html")


@kasta_cmd(
    pattern="info(?: |$)(.*)",
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    user, _ = await get_user(kst, 1)
    if user:
        user_id = user.id
    else:
        user_id = kst.client.uid
    try:
        full = await kst.client(GetFullUserRequest(user_id))
        full_user = full.full_user
        user = full.users[0]
    except Exception as err:
        return await msg.eor(f"**ERROR:**\n`{err}`")
    user_photos = (await kst.client.get_profile_photos(user_id, limit=0)).total or 0
    first_name = html.escape(user.first_name).replace("\u2060", "")
    last_name = (
        user.last_name and "\n ├ <b>Last Name:</b> <code>{}</code>".format(user.last_name.replace("\u2060", "")) or ""
    )
    username = user.username and "\n ├ <b>Username:</b> @{}".format(user.username) or ""
    user_bio = full_user.about and html.escape(full_user.about) or ""
    user_status = get_user_status(user)
    dc_id = user.photo and user.photo.dc_id or 0
    is_rose_fban = await get_rose_fban(kst, user_id)
    is_spamwatch_banned = await get_spamwatch_banned(kst, user_id)
    is_cas_banned = await get_cas_banned(kst, user_id)
    caption = """<b><u>USER INFORMATION</u></b>
 ├ <b>ID:</b> <code>{}</code>
 ├ <b>DC ID:</b> <code>{}</code>
 ├ <b>First Name:</b> <code>{}</code>{}{}
 ├ <b>User Profile:</b> <a href='tg://user?id={}'>Link</a>
 ├ <b>Number Of Pics:</b> <code>{}</code>
 ├ <b>Last Seen:</b> <code>{}</code>
 ├ <b>Is Mutual Contact:</b> <code>{}</code>
 ├ <b>Is Blocked User:</b> <code>{}</code>
 ├ <b>Is Private Forward:</b> <code>{}</code>
 ├ <b>Is Fake:</b> <code>{}</code>
 ├ <b>Is Scam:</b> <code>{}</code>
 ├ <b>Is Restricted:</b> <code>{}</code>
 ├ <b>Is Verified:</b> <code>{}</code>
 ├ <b>Is Support:</b> <code>{}</code>
 ├ <b>Is Bot:</b> <code>{}</code>
 ├ <b>Is Deleted:</b> <code>{}</code>
 ├ <b>Is Rose Fban:</b> <code>{}</code>
 ├ <b>Is SpamWatch Banned:</b> <code>{}</code>
 ├ <b>Is CAS Banned:</b> <code>{}</code>
 ├ <b>Groups In Common:</b> <code>{}</code>
 └ <b>Bio:</b>\n<pre>{}</pre>
""".format(
        user_id,
        dc_id,
        first_name,
        last_name,
        username,
        user_id,
        user_photos,
        user_status,
        humanbool(user.mutual_contact),
        humanbool(full_user.blocked),
        humanbool(bool(full_user.private_forward_name)),
        humanbool(user.fake),
        humanbool(user.scam),
        humanbool(user.restricted),
        humanbool(user.verified),
        humanbool(user.support),
        humanbool(user.bot),
        humanbool(user.deleted),
        humanbool(is_rose_fban),
        humanbool(is_spamwatch_banned),
        humanbool(is_cas_banned),
        full_user.common_chats_count,
        user_bio,
    )
    try:
        await kst.client.send_file(
            kst.chat_id,
            file=full_user.profile_photo,
            caption=caption,
            force_document=False,
            allow_cache=True,
            reply_to=kst.reply_to_msg_id,
            parse_mode="html",
            silent=True,
        )
        await msg.try_delete()
    except BaseException:
        await msg.eor(caption, parse_mode="html")


@kasta_cmd(
    pattern="groupinfo(?: |$)(.*)",
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    match = kst.pattern_match.group(1)
    if match:
        try:
            group = await kst.client.get_peer_id(match)
        except Exception as err:
            return await msg.eor(f"**ERROR:**\n`{err}`")
    else:
        group = kst.chat_id
    try:
        entity = await kst.client.get_entity(group)
    except Exception as err:
        return await msg.eor(f"**ERROR:**\n`{err}`")
    if isinstance(entity, User):
        return
    photo, caption = await get_chat_info(entity, kst)
    if not photo:
        return await msg.eor(caption, parse_mode="html")
    try:
        await kst.client.send_file(
            kst.chat_id,
            file=photo,
            caption=caption[:1024],
            force_document=False,
            allow_cache=True,
            reply_to=kst.reply_to_msg_id,
            parse_mode="html",
            silent=True,
        )
        await msg.try_delete()
    except BaseException:
        await msg.eor(caption, parse_mode="html")


async def get_chat_info(chat, kst):
    if isinstance(chat, Channel):
        chat_info = await kst.client(GetFullChannelRequest(chat))
    elif isinstance(chat, Chat):
        chat_info = await kst.client(GetFullChatRequest(chat))
    else:
        return await kst.eor("`Use this for Group/Channel.`")
    full = chat_info.full_chat
    chat_photo = full.chat_photo
    broadcast = getattr(chat, "broadcast", False)
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat.title
    try:
        msg_info = await kst.client(
            GetHistoryRequest(
                peer=chat.id,
                offset_id=0,
                offset_date=None,
                add_offset=-0,
                limit=0,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
    except BaseException:
        msg_info = None
    first_msg_valid = bool(msg_info and msg_info.messages and msg_info.messages[0].id == 1)
    creator_valid = bool(first_msg_valid and msg_info.users)
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = (
        msg_info.users[0].first_name if creator_valid and msg_info.users[0].first_name else "Deleted Account"
    )
    creator_username = msg_info.users[0].username if creator_valid and msg_info.users[0].username else None
    created = msg_info.messages[0].date if first_msg_valid else None
    if not isinstance(chat.photo, ChatPhotoEmpty):
        dc_id = chat.photo.dc_id
    else:
        dc_id = 0
    restricted_users = getattr(full, "banned_count", None)
    members = getattr(full, "participants_count", chat.participants_count)
    admins = getattr(full, "admins_count", None)
    banned_users = getattr(full, "kicked_count", None)
    members_online = getattr(full, "online_count", 0)
    group_stickers = full.stickerset.title if getattr(full, "stickerset", None) else None
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = getattr(full, "read_inbox_max_id", None)
    messages_sent_alt = getattr(full, "read_outbox_max_id", None)
    exp_count = getattr(full, "pts", None)
    supergroup = "<b>Yes</b>" if getattr(chat, "megagroup", None) else "No"
    creator_username = "@{}".format(creator_username) if creator_username else None
    if not admins:
        try:
            participants_admins = await kst.client(
                GetParticipantsRequest(
                    channel=chat.id,
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=0,
                    hash=0,
                )
            )
            admins = participants_admins.count if participants_admins else None
        except BaseException:
            pass
    caption = "<b><u>CHAT INFO</u></b>\n"
    caption += f" ├ <b>ID:</b> <code>{chat.id}</code>\n"
    if chat_title:
        caption += f" ├ <b>{chat_type} Name:</b> <code>{chat_title}</code>\n"
    if chat.username:
        caption += f" ├ <b>Link:</b> @{chat.username}\n"
    else:
        caption += f" ├ <b>{chat_type} type:</b> Private\n"
    if creator_username:
        caption += f" ├ <b>Creator:</b> {creator_username}\n"
    elif creator_valid:
        caption += f' ├ <b>Creator:</b> <a href="tg://user?id={creator_id}">{creator_firstname}</a>\n'
    if created:
        caption += f" ├ <b>Created:</b> <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f" ├ <b>Created:</b> <code>{chat.date.date().strftime('%b %d, %Y')} - {chat.date.time()}</code>\n"
    caption += f" ├ <b>DC ID:</b> <code>{dc_id}</code>\n"
    if exp_count:
        chat_level = int((1 + math.sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f" ├ <b>{chat_type} Level:</b> <code>{chat_level}</code>\n"
    if messages_viewable:
        caption += f" ├ <b>Viewable Messages:</b> <code>{messages_viewable}</code>\n"
    if messages_sent:
        caption += f" ├ <b>Messages Sent:</b> <code>{messages_sent}</code>\n"
    elif messages_sent_alt:
        caption += f" ├ <b>Messages Sent:</b> <code>{messages_sent_alt}</code>\n"
    if members:
        caption += f" ├ <b>Members:</b> <code>{members}</code>\n"
    if admins:
        caption += f" ├ <b>Administrators:</b> <code>{admins}</code>\n"
    if full.bot_info:
        caption += f" ├ <b>Bots:</b> <code>{len(full.bot_info)}</code>\n"
    if members_online:
        caption += f" ├ <b>Currently Online:</b> <code>{members_online}</code>\n"
    if restricted_users:
        caption += f" ├ <b>Restricted Users:</b> <code>{restricted_users}</code>\n"
    if banned_users:
        caption += f" ├ <b>Banned Users:</b> <code>{banned_users}</code>\n"
    if group_stickers:
        caption += f' ├ <b>{chat_type} Stickers:</b> <a href="t.me/addstickers/{full.stickerset.short_name}">{group_stickers}</a>\n'
    if not broadcast:
        if getattr(chat, "slowmode_enabled", None):
            caption += f" ├ <b>Slow Mode:</b> <code>{full.slowmode_seconds}s</code>\n"
        else:
            caption += f" ├ <b>Supergroup:</b> {supergroup}\n"
    if getattr(chat, "restricted", None):
        caption += f" ├ <b>Restricted:</b> {chat.restricted}\n"
        rist = chat.restriction_reason[0]
        caption += f"   > Platform: {rist.platform}\n"
        caption += f"   > Reason: {rist.reason}\n"
        caption += f"   > Text: {rist.text}\n"
    if getattr(chat, "scam", None):
        caption += " ├ <b>Scam:</b> <b>Yes</b>\n"
    if getattr(chat, "verified", None):
        caption += f" ├ <b>Verified By Telegram:</b> <code>Yes</code>\n"
    if full.about:
        caption += f" └ <b>Description:</b>\n<pre>{full.about}</pre>"
    return chat_photo, caption


@AsyncTTL(time_to_live=(30 * 10), maxsize=512)  # 5 mins
async def get_total_created(kst, bot: str, command: str) -> int:
    total = 0
    resp = None
    async with kst.client.conversation(bot) as conv:
        try:
            await conv.send_message(command)
        except YouBlockedUserError:
            await kst.client(UnblockRequest(bot))
            await conv.send_message(command)
        resp = await conv.get_response()
        await resp.mark_read(clear_mentions=True)
    if not resp:
        total = 0
    elif resp and resp.message.lower().startswith("you don't"):
        total = 0
    elif resp.message.lower().startswith("choose"):
        for rows in resp.reply_markup.rows:
            if rows.buttons:
                for _ in rows.buttons:
                    total += 1
            else:
                total += 1
    return total


async def get_rose_fban(kst, user_id: int) -> bool:
    global ROSE_LANG_CACHE, ROSE_STAT_CACHE
    if user_id in ROSE_STAT_CACHE:
        return ROSE_STAT_CACHE.get(user_id)
    rose = "@MissRose_bot"
    resp = None
    async with kst.client.conversation(rose) as conv:
        try:
            if not ROSE_LANG_CACHE.get("lang"):
                await conv.send_message("/setlang EN-GB")
                await conv.get_response()
            await conv.send_message(f"/fedstat {user_id}")
        except YouBlockedUserError:
            await kst.client(UnblockRequest(rose))
            if not ROSE_LANG_CACHE.get("lang"):
                await conv.send_message("/setlang EN-GB")
                await conv.get_response()
            await conv.send_message(f"/fedstat {user_id}")
        while True:
            await asyncio.sleep(1.5)
            resp = await conv.get_response()
            if not resp.message.lower().startswith("checking fbans"):
                break
        if resp:
            await resp.mark_read(clear_mentions=True)
        ROSE_LANG_CACHE["lang"] = True
    if not resp:
        ROSE_STAT_CACHE[user_id] = False
        return False
    elif "hasn't been banned" in resp.message:
        ROSE_STAT_CACHE[user_id] = False
        return False
    elif "to be banned" in resp.message:
        ROSE_STAT_CACHE[user_id] = True
        return True
    ROSE_STAT_CACHE[user_id] = False
    return False


async def get_spamwatch_banned(kst, user_id: int) -> bool:
    global SPAMWATCH_CACHE
    if user_id in SPAMWATCH_CACHE:
        return SPAMWATCH_CACHE.get(user_id)
    url = f"https://notapi.vercel.app/api/spamwatch?id={user_id}"
    res = await Searcher(url=url, re_json=True)
    if not res:
        SPAMWATCH_CACHE[user_id] = False
        return False
    SPAMWATCH_CACHE[user_id] = bool(res.get("id"))
    return bool(res.get("id"))


async def get_cas_banned(kst, user_id: int) -> bool:
    global CAS_CACHE
    if user_id in CAS_CACHE:
        return CAS_CACHE.get(user_id)
    url = f"https://api.cas.chat/check?user_id={user_id}"
    res = await Searcher(url=url, re_json=True)
    if not res:
        CAS_CACHE[user_id] = False
        return False
    CAS_CACHE[user_id] = res.get("ok")
    return res.get("ok")


async def sglist(text) -> tuple:
    for x in text:
        if x.startswith("🔗"):
            text.remove(x)
    part = 0
    for x in text:
        if x.lower().startswith("username history"):
            break
        part += 1
    usernames = text[part:]
    names = text[:part]
    return (names, usernames)


HELP.update(
    {
        "info": [
            "Info",
            """❯ `{i}sg <reply/username/id>`
Get names and usernames by sangmata.

❯ `{i}created <reply/username/id>`
Get creation date by creationdatebot.

❯ `{i}total <reply/username>`
Get total user messages.

❯ `{i}stats`
Show your profile stats.

❯ `{i}info <reply/username/id>`
Get mentioned user info, it also get Rose Fban, SpamWatch Banned, CAS Banned, etc. Per ids is cached in 2 minutes.

❯ `{i}groupinfo <current/username>`
Get details information of current group or mentioned group.
""",
        ]
    }
)
