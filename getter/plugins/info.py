# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from html import escape
from math import sqrt
from time import monotonic

from cachetools import LRUCache, TTLCache
from telethon import events
from telethon.errors import FloodWaitError, YouBlockedUserError
from telethon.tl import custom, functions as fun, types as typ

from . import (
    Fetch,
    all_allow,
    all_gban,
    all_gmute,
    display_name,
    formatx_send,
    get_user_status,
    humanbool,
    is_allow,
    is_gban,
    is_gmute,
    jdata,
    kasta_cmd,
    parse_pre,
    plugins_help,
)

SG_BOT = "SangMata_BOT"
CREATED_BOT = "creationdatebot"
ROSE_BOT = "MissRose_bot"
_TOTAL_BOT_CACHE = TTLCache(maxsize=100, ttl=120)  # 2 mins
_CREATED_CACHE = TTLCache(maxsize=100, ttl=120)  # 2 mins
_ROSE_LANG_CACHE = LRUCache(maxsize=100)
_ROSE_STAT_CACHE = TTLCache(maxsize=100, ttl=120)  # 2 mins
_SPAMWATCH_CACHE = TTLCache(maxsize=100, ttl=120)  # 2 mins
_CAS_CACHE = TTLCache(maxsize=100, ttl=120)  # 2 mins


@kasta_cmd(
    pattern="dc$",
)
async def _(kst):
    dc = await kst.client(fun.help.GetNearestDcRequest())
    await kst.eor(
        f"├  **Country:** `{dc.country}`\n"
        f"├  **Nearest Datacenter:** `{dc.nearest_dc}`\n"
        f"└  **This Datacenter:** `{dc.this_dc}`",
    )


@kasta_cmd(
    pattern="sg(?: |$)(.*)",
    edited=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    texts = []
    resp = None
    await ga.unblock(SG_BOT)
    async with ga.conversation(SG_BOT) as conv:
        await conv.send_message(str(user.id))
        while True:
            try:
                resp = await conv.get_response(timeout=2)
            except asyncio.exceptions.TimeoutError:
                break
            texts.append(resp.message)
        if resp:
            await resp.read()
    if not texts:
        return await yy.eod("`Cannot get any records.`")
    if any(_ for _ in texts if _.lower().startswith("no data")):
        return await yy.eod("`Got no records.`")
    for txt in texts:
        await yy.sod(
            txt,
            force_reply=True,
            silent=True,
            parse_mode=parse_pre,
        )
        await asyncio.sleep(0.5)


@kasta_cmd(
    pattern="created(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    user, _ = await ga.get_user(kst)
    user_id = user.id if user else ga.uid
    async with ga.conversation(CREATED_BOT) as conv:
        resp = await conv_created(conv, user_id)
    if not resp:
        return await yy.eod("`Bot did not respond.`")
    await ga.delete_chat(CREATED_BOT, revoke=True)
    await yy.eor(resp, parse_mode=parse_pre)


@kasta_cmd(
    pattern="total(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    match = kst.pattern_match.group(1)
    if match:
        from_user = match
    elif kst.is_reply:
        from_user = (await kst.get_reply_message()).sender_id
    else:
        from_user = "me"
    chat = await kst.get_input_chat()
    try:
        msg = await ga.get_messages(
            chat,
            limit=0,
            from_user=from_user,
        )
    except FloodWaitError as fw:
        await asyncio.sleep(fw.seconds + 10)
        msg = await ga.get_messages(
            chat,
            limit=0,
            from_user=from_user,
        )
    except BaseException:
        return await kst.try_delete()
    whois = display_name(await ga.get_entity(from_user))
    await yy.eor(f"Total messages from <code>{whois}</code> is <code>{msg.total}</code>", parse_mode="html")


@kasta_cmd(
    pattern="stats?$",
)
async def _(kst):
    start_time = monotonic()
    ga = kst.client
    private_chats = 0
    bots = 0
    groups = 0
    channels = 0
    admin_groups = 0
    creator_groups = 0
    admin_channels = 0
    creator_channels = 0
    unread = 0
    unread_mentions = 0
    archived = 0
    dialog: custom.Dialog
    yy = await kst.eor("`Collecting Stats...`")
    async for dialog in ga.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, typ.Channel) and entity.broadcast:
            channels += 1
            if entity.creator or entity.admin_rights:
                admin_channels += 1
            if entity.creator:
                creator_channels += 1
        elif (isinstance(entity, typ.Channel) and entity.megagroup) or isinstance(entity, typ.Chat):
            groups += 1
            if entity.creator or entity.admin_rights:
                admin_groups += 1
            if entity.creator:
                creator_groups += 1
        elif isinstance(entity, typ.User):
            private_chats += 1
            if entity.bot:
                bots += 1
        unread += dialog.unread_count
        unread_mentions += dialog.unread_mentions_count
        if dialog.archived:
            archived += 1
    try:
        bl_count = (await ga(fun.contacts.GetBlockedRequest(1, 0))).count
    except BaseException:
        bl_count = 0
    try:
        gs_count = len((await ga(fun.messages.GetSavedGifsRequest(0))).gifs)
    except BaseException:
        gs_count = 0
    try:
        sp_count = len((await ga(fun.messages.GetAllStickersRequest(0))).sets)
    except BaseException:
        sp_count = 0
    sc_count = await get_total_bot(kst, "Stickers", "/stats")
    bc_count = await get_total_bot(kst, "BotFather", "/setcommands")
    gbanned_users = len(await all_gban())
    gmuted_users = len(await all_gmute())
    sudo_users = len(await jdata.sudo_users())
    allowed_users = len(await all_allow())
    stop_time = monotonic() - start_time
    graph = """<b>Stats for {}</b>
├  <b>Private:</b> <code>{}</code>
┊  ├  <b>Users:</b> <code>{}</code>
┊  ├  <b>Bots:</b> <code>{}</code>
├  <b>Groups:</b> <code>{}</code>
├  <b>Channels:</b> <code>{}</code>
├  <b>Admin Groups:</b> <code>{}</code>
┊  ├  <b>Creator:</b> <code>{}</code>
┊  ├  <b>Admin Rights:</b> <code>{}</code>
├  <b>Admin Channels:</b> <code>{}</code>
┊  ├  <b>Creator:</b> <code>{}</code>
┊  ├  <b>Admin Rights:</b> <code>{}</code>
├  <b>Unread:</b> <code>{}</code>
├  <b>Unread Mentions:</b> <code>{}</code>
├  <b>Archived:</b> <code>{}</code>
├  <b>Blocked Users:</b> <code>{}</code>
├  <b>Gifs Saved:</b> <code>{}</code>
├  <b>Stickers Pack Installed:</b> <code>{}</code>
├  <b>Stickers Pack Created:</b> <code>{}</code>
├  <b>Bots Created:</b> <code>{}</code>
├  <b>Gbanned Users:</b> <code>{}</code>
├  <b>Gmuted Users:</b> <code>{}</code>
├  <b>Sudo Users:</b> <code>{}</code>
├  <b>Allowed Users PM:</b> <code>{}</code>
└  <b>It Took:</b> <code>{}s</code>""".format(
        ga.full_name,
        private_chats,
        private_chats - bots,
        bots,
        groups,
        channels,
        admin_groups,
        creator_groups,
        admin_groups - creator_groups,
        admin_channels,
        creator_channels,
        admin_channels - creator_channels,
        unread,
        unread_mentions,
        archived,
        bl_count,
        gs_count,
        sp_count,
        sc_count,
        bc_count,
        gbanned_users,
        gmuted_users,
        sudo_users,
        allowed_users,
        f"{stop_time:.3f}",
    )
    await yy.sod(graph, parse_mode="html")


@kasta_cmd(
    pattern="ids?(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    user_id = None
    match = kst.pattern_match.group(1)
    if match:
        try:
            user_id = await ga.get_id(match)
        except BaseException:
            pass
    chat_id = kst.chat_id or kst.from_id
    if kst.is_reply:
        user_id, msg_id = (await kst.get_reply_message()).sender_id, kst.reply_to_msg_id
        if kst.is_private:
            ids = f"├  **User ID:** `{user_id}`\n"
        else:
            ids = f"├  **Chat ID:** `{chat_id}`\n"
            ids += f"├  **User ID:** `{user_id}`\n"
        ids += f"└  **Message ID:** `{msg_id}`"
    else:
        if user_id:
            ids = f"├  **User ID:** `{user_id}`\n"
            ids += f"├  **Chat ID:** `{chat_id}`\n"
        else:
            ids = "├  **User ID:** " if kst.is_private else "├  **Chat ID:** "
            ids += f"`{chat_id}`\n"
        ids += f"└  **Message ID:** `{kst.id}`"
    await kst.eor(ids)


@kasta_cmd(
    pattern="cc(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot get cc to myself.`", time=3)
    try:
        chat = await ga(
            fun.messages.GetCommonChatsRequest(
                user.id,
                max_id=0,
                limit=0,
            )
        )
        collect = [_.title + "\n" for _ in chat.chats]
        whois = display_name(await ga.get_entity(user.id))
        if collect:
            text = f"<b>{len(collect)} Groups in common with:</b> <code>{whois}</code>\n" + "".join(collect)
        else:
            text = f"<b>0 Groups in common with:</b> <code>{whois}</code>"
        await yy.eor(text, parts=True, parse_mode="html")
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="infos?(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    target, args = await ga.get_user(kst)
    if target:
        user_id = target.id
        opts = args.split(" ")
        is_full = any(_ in opts[0].lower() for _ in ("-f", "full"))
    else:
        user_id = ga.uid
        is_full = True
    try:
        full = await ga(fun.users.GetFullUserRequest(user_id))
        full_user = full.full_user
        user = full.users[0]
    except ValueError:
        return await yy.eod("`Cannot fetch user info.`")
    except Exception as err:
        return await yy.eor(formatx_send(err), parse_mode="html")
    created = ""
    try:
        async with ga.conversation(CREATED_BOT) as conv:
            resp = await conv_created(conv, user_id)
        created = f"\n├  <b>Created:</b> <code>{resp}</code>"
        await ga.delete_dialog(CREATED_BOT, revoke=True)
    except BaseException:
        pass
    dc_id = (user.photo and user.photo.dc_id) or 0
    first_name = escape(user.first_name).replace("\u2060", "")
    last_name = (
        user.last_name and "\n├  <b>Last Name:</b> <code>{}</code>".format(user.last_name.replace("\u2060", ""))
    ) or ""
    username = (user.username and f"\n├  <b>Username:</b> @{user.username}") or ""
    user_pictures = (await ga.get_profile_photos(user_id, limit=0)).total or 0
    user_status = get_user_status(user)
    user_bio = escape(full_user.about or "")
    if not is_full:
        caption = f"""<b><u>USER INFORMATION</u></b>
├  <b>ID:</b> <code>{user_id}</code>{created}
├  <b>DC ID:</b> <code>{dc_id}</code>
├  <b>First Name:</b> <code>{first_name}</code>{last_name}{username}
├  <b>Profile:</b> <a href=tg://user?id={user_id}>Link</a>
├  <b>Pictures:</b> <code>{user_pictures}</code>
├  <b>Last Seen:</b> <code>{user_status}</code>
├  <b>Is Premium:</b> <code>{humanbool(user.premium)}</code>
├  <b>Is Bot:</b> <code>{humanbool(user.bot)}</code>
├  <b>Is Blocked:</b> <code>{humanbool(full_user.blocked)}</code>
├  <b>Is Contact:</b> <code>{humanbool(user.contact)}</code>
├  <b>Is Deleted:</b> <code>{humanbool(user.deleted)}</code>
├  <b>Is Private Forward:</b> <code>{humanbool(full_user.private_forward_name)}</code>
├  <b>Is Scam:</b> <code>{humanbool(user.scam)}</code>
├  <b>Groups In Common:</b> <code>{full_user.common_chats_count}</code>
└  <b>Bio:</b>
<pre>{user_bio}</pre>"""
    else:
        is_rose_fban = await get_rose_fban(kst, user_id)
        is_spamwatch_banned = await get_spamwatch_banned(kst, user_id)
        is_cas_banned = await get_cas_banned(kst, user_id)
        is_gbanned = bool(await is_gban(user_id))
        is_gmuted = bool(await is_gmute(user_id))
        is_sudo = user_id in await jdata.sudo_users()
        is_allowed = bool(await is_allow(user_id))
        caption = """<b><u>USER INFORMATION</u></b>
├  <b>ID:</b> <code>{}</code>{}
├  <b>DC ID:</b> <code>{}</code>
├  <b>First Name:</b> <code>{}</code>{}{}
├  <b>Language:</b> <code>{}</code>
├  <b>Profile:</b> <a href=tg://user?id={}>Link</a>
├  <b>Pictures:</b> <code>{}</code>
├  <b>Last Seen:</b> <code>{}</code>
├  <b>Is Premium:</b> <code>{}</code>
├  <b>Is Bot:</b> <code>{}</code>
├  <b>Is Blocked:</b> <code>{}</code>
├  <b>Is Contact:</b> <code>{}</code>
├  <b>Is Deleted:</b> <code>{}</code>
├  <b>Is Private Forward:</b> <code>{}</code>
├  <b>Is Scam:</b> <code>{}</code>
├  <b>Is Fake:</b> <code>{}</code>
├  <b>Is Restricted:</b> <code>{}</code>
├  <b>Is Support:</b> <code>{}</code>
├  <b>Is Verified:</b> <code>{}</code>
├  <b>Is Mutual Contact:</b> <code>{}</code>
├  <b>Is Emoji Status:</b> <code>{}</code>
├  <b>Is Rose Fban:</b> <code>{}</code>
├  <b>Is SpamWatch Banned:</b> <code>{}</code>
├  <b>Is CAS Banned:</b> <code>{}</code>
├  <b>Is Gbanned:</b> <code>{}</code>
├  <b>Is Gmuted:</b> <code>{}</code>
├  <b>Is Sudo:</b> <code>{}</code>
├  <b>Is Allowed PM:</b> <code>{}</code>
├  <b>Groups In Common:</b> <code>{}</code>
└  <b>Bio:</b>
<pre>{}</pre>""".format(
            user_id,
            created,
            dc_id,
            first_name,
            last_name,
            username,
            user.lang_code or "en",
            user_id,
            user_pictures,
            user_status,
            humanbool(user.premium),
            humanbool(user.bot),
            humanbool(full_user.blocked),
            humanbool(user.contact),
            humanbool(user.deleted),
            humanbool(full_user.private_forward_name),
            humanbool(user.scam),
            humanbool(user.fake),
            humanbool(user.restricted),
            humanbool(user.support),
            humanbool(user.verified),
            humanbool(user.mutual_contact),
            humanbool(bool(user.emoji_status)),
            humanbool(is_rose_fban),
            humanbool(is_spamwatch_banned),
            humanbool(is_cas_banned),
            humanbool(is_gbanned),
            humanbool(is_gmuted),
            humanbool(is_sudo),
            humanbool(is_allowed),
            full_user.common_chats_count,
            user_bio,
        )
    try:
        await yy.eor(
            caption,
            file=full_user.profile_photo,
            force_document=False,
            parse_mode="html",
        )
    except BaseException:
        await yy.eor(caption, parse_mode="html")


@kasta_cmd(
    pattern="chatstats?(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    where = await ga.get_text(kst)
    if where:
        try:
            chat_id = await ga.get_id(where)
        except Exception as err:
            return await yy.eor(formatx_send(err), parse_mode="html")
    else:
        chat_id = kst.chat_id
    total = (await ga.get_messages(chat_id, limit=0)).total
    photo = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterPhotos())).total
    video = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterVideo())).total
    music = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterMusic())).total
    voice_note = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterVoice())).total
    video_note = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterRoundVideo())).total
    files = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterDocument())).total
    urls = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterUrl())).total
    gifs = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterGif())).total
    maps = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterGeo())).total
    contact = (await ga.get_messages(chat_id, limit=0, filter=typ.InputMessagesFilterContacts())).total
    text = f"""<b><u>{total} TOTAL MESSAGES</u></b>
├  <b>Photo:</b> <code>{photo}</code>
├  <b>Video:</b> <code>{video}</code>
├  <b>Music:</b> <code>{music}</code>
├  <b>Voice Note:</b> <code>{voice_note}</code>
├  <b>Video Note:</b> <code>{video_note}</code>
├  <b>Document:</b> <code>{files}</code>
├  <b>URL:</b> <code>{urls}</code>
├  <b>Gif:</b> <code>{gifs}</code>
├  <b>Map:</b> <code>{maps}</code>
└  <b>Contact:</b> <code>{contact}</code>"""
    await yy.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="chatinfos?(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    where = await ga.get_text(kst)
    if where:
        try:
            chat = await ga.get_id(where)
        except Exception as err:
            return await yy.eor(formatx_send(err), parse_mode="html")
    else:
        chat = kst.chat_id
    try:
        entity = await ga.get_entity(chat)
    except Exception as err:
        return await yy.eor(formatx_send(err), parse_mode="html")
    photo, caption = await get_chat_info(kst, entity)
    if not photo:
        return await yy.eor(caption, parse_mode="html")
    try:
        await yy.eor(
            caption,
            file=photo,
            force_document=False,
            parse_mode="html",
        )
    except BaseException:
        await yy.eor(caption, parse_mode="html")


async def get_chat_info(kst, chat):
    ga = kst.client
    if isinstance(chat, typ.Channel):
        chat_info = await ga(fun.channels.GetFullChannelRequest(chat))
    elif isinstance(chat, typ.Chat):
        chat_info = await ga(fun.messages.GetFullChatRequest(chat))
    else:
        return await kst.eod("`Use this for group/channel.`")
    full = chat_info.full_chat
    chat_photo = full.chat_photo
    broadcast = getattr(chat, "broadcast", False)
    chat_type = "Channel" if broadcast else "Group"
    chat_title = chat.title
    try:
        msg_info = await ga(
            fun.messages.GetHistoryRequest(
                chat.id,
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
    dc_id = chat.photo.dc_id if not isinstance(chat.photo, typ.ChatPhotoEmpty) else 0
    restricted_users = getattr(full, "banned_count", None)
    members = getattr(full, "participants_count", chat.participants_count)
    admins = getattr(full, "admins_count", None)
    banned_users = getattr(full, "kicked_count", None)
    members_online = getattr(full, "online_count", 0)
    group_stickers = full.stickerset.title if getattr(full, "stickerset", None) else None
    msgs_viewable = msg_info.count if msg_info else None
    msgs_sent = getattr(full, "read_inbox_max_id", None)
    msgs_sent_alt = getattr(full, "read_outbox_max_id", None)
    exp_count = getattr(full, "pts", None)
    supergroup = humanbool(getattr(chat, "megagroup", None))
    creator_username = f"@{creator_username}" if creator_username else None
    if not admins:
        try:
            admin_rights = await ga(
                fun.channels.GetParticipantsRequest(
                    chat.id,
                    filter=typ.ChannelParticipantsAdmins(),
                    offset=0,
                    limit=0,
                    hash=0,
                )
            )
            admins = admin_rights.count if admin_rights else None
        except BaseException:
            pass
    caption = "<b><u>CHAT INFORMATION</u></b>\n"
    caption += f"├  <b>ID:</b> <code>{chat.id}</code>\n"
    if chat_title:
        caption += f"├  <b>{chat_type} Name:</b> <code>{chat_title}</code>\n"
    if chat.username:
        caption += f"├  <b>Username:</b> @{chat.username}\n"
    else:
        caption += f"├  <b>{chat_type} Type:</b> Private\n"
    if creator_username:
        caption += f"├  <b>Creator:</b> {creator_username}\n"
    elif creator_valid:
        caption += f"├  <b>Creator:</b> <a href=tg://user?id={creator_id}>{creator_firstname}</a>\n"
    if created:
        caption += f"├  <b>Created:</b> <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f"├  <b>Created:</b> <code>{chat.date.date().strftime('%b %d, %Y')} - {chat.date.time()}</code>\n"
    caption += f"├  <b>DC ID:</b> <code>{dc_id}</code>\n"
    if exp_count:
        chat_level = int((1 + sqrt(1 + 7 * exp_count / 14)) / 2)
        caption += f"├  <b>{chat_type} Level:</b> <code>{chat_level}</code>\n"
    if msgs_viewable:
        caption += f"├  <b>Viewable Messages:</b> <code>{msgs_viewable}</code>\n"
    if msgs_sent:
        caption += f"├  <b>Messages Sent:</b> <code>{msgs_sent}</code>\n"
    elif msgs_sent_alt:
        caption += f"├  <b>Messages Sent:</b> <code>{msgs_sent_alt}</code>\n"
    if members:
        caption += f"├  <b>Members:</b> <code>{members}</code>\n"
    if admins:
        caption += f"├  <b>Administrators:</b> <code>{admins}</code>\n"
    if full.bot_info:
        caption += f"├  <b>Bots:</b> <code>{len(full.bot_info)}</code>\n"
    if members_online:
        caption += f"├  <b>Currently Online:</b> <code>{members_online}</code>\n"
    if restricted_users:
        caption += f"├  <b>Restricted Users:</b> <code>{restricted_users}</code>\n"
    if banned_users:
        caption += f"├  <b>Banned Users:</b> <code>{banned_users}</code>\n"
    if group_stickers:
        caption += f"├  <b>{chat_type} Stickers:</b> <a href='t.me/addstickers/{full.stickerset.short_name}'>{group_stickers}</a>\n"
    if not broadcast:
        if getattr(chat, "slowmode_enabled", None):
            caption += f"├  <b>Slow Mode:</b> <code>{full.slowmode_seconds}s</code>\n"
        else:
            caption += f"├  <b>Supergroup:</b> <code>{supergroup}</code>\n"
    if getattr(chat, "restricted", None):
        caption += f"├  <b>Restricted:</b> {chat.restricted}\n"
        rist = chat.restriction_reason[0]
        caption += f"┊  ├  <b>Platform:</b> {rist.platform}\n"
        caption += f"┊  ├  <b>Reason:</b> {rist.reason}\n"
        caption += f"┊  ├  <b>Text:</b> {rist.text}\n"
    if getattr(chat, "scam", None):
        caption += "├  <b>Scam:</b> <code>yes</code>\n"
    if getattr(chat, "verified", None):
        caption += "├  <b>Verified By Telegram:</b> <code>yes</code>\n"
    about = escape(full.about or "")
    caption += f"└  <b>Description:</b>\n<pre>{about}</pre>"
    return chat_photo, caption


async def conv_created(conv, user_id):
    if user_id in _CREATED_CACHE:
        return _CREATED_CACHE.get(user_id)
    try:
        resp = conv.wait_event(
            events.NewMessage(
                incoming=True,
                from_users=conv.chat_id,
            ),
        )
        yy = await conv.send_message(f"/id {user_id}")
        resp = await resp
        await yy.try_delete()
        await resp.read(
            clear_mentions=True,
            clear_reactions=True,
        )
        created = getattr(resp.message, "message", None)
        _CREATED_CACHE[user_id] = created
        return created
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_created(conv, user_id)


async def conv_total_bot(conv, command):
    try:
        resp = conv.wait_event(
            events.NewMessage(
                incoming=True,
                from_users=conv.chat_id,
            ),
        )
        yy = await conv.send_message(command)
        resp = await resp
        await yy.try_delete()
        await resp.read(
            clear_mentions=True,
            clear_reactions=True,
        )
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_total_bot(conv, command)


async def get_total_bot(kst, bot: str, command: str) -> int:
    ga = kst.client
    in_cache = bot.lower()
    if in_cache in _TOTAL_BOT_CACHE:
        return _TOTAL_BOT_CACHE.get(in_cache)
    total = 0
    async with ga.conversation(bot) as conv:
        resp = await conv_total_bot(conv, command)
    if (not resp) or (resp and resp.message.message.lower().startswith("you don't")):
        total = 0
    elif resp.message.message.lower().startswith("choose"):
        for rows in resp.reply_markup.rows:
            if rows.buttons:
                for _ in rows.buttons:
                    total += 1
            else:
                total += 1
    _TOTAL_BOT_CACHE[in_cache] = total
    await resp.try_delete()
    return total


async def get_rose_fban(kst, user_id: int) -> bool:
    ga = kst.client
    if user_id in _ROSE_STAT_CACHE:
        return _ROSE_STAT_CACHE.get(user_id)
    resp = None
    async with ga.conversation(ROSE_BOT) as conv:
        try:
            if not _ROSE_LANG_CACHE.get("lang"):
                yy = await conv.send_message("/setlang EN-GB")
                lang = await conv.get_response()
                await yy.try_delete()
                await lang.try_delete()
            yy = await conv.send_message(f"/fedstat {user_id}")
        except YouBlockedUserError:
            await conv._client.unblock(conv.chat_id)
            if not _ROSE_LANG_CACHE.get("lang"):
                yy = await conv.send_message("/setlang EN-GB")
                lang = await conv.get_response()
                await yy.try_delete()
                await lang.try_delete()
            yy = await conv.send_message(f"/fedstat {user_id}")
        while True:
            await asyncio.sleep(1.5)
            resp = await conv.get_response()
            await yy.try_delete()
            if not resp.message.lower().startswith("checking fbans"):
                break
        if resp:
            await resp.read(
                clear_mentions=True,
                clear_reactions=True,
            )
        _ROSE_LANG_CACHE["lang"] = True
    if (not resp) or ("hasn't been banned" in resp.message.lower()):
        _ROSE_STAT_CACHE[user_id] = False
        await resp.try_delete()
        return False
    if "to be banned" in resp.message.lower():
        _ROSE_STAT_CACHE[user_id] = True
        await resp.try_delete()
        return True
    _ROSE_STAT_CACHE[user_id] = False
    await resp.try_delete()
    return False


async def get_spamwatch_banned(kst, user_id: int) -> bool:
    if user_id in _SPAMWATCH_CACHE:
        return _SPAMWATCH_CACHE.get(user_id)
    url = f"https://notapi.vercel.app/api/spamwatch?id={user_id}"
    res = await Fetch(url, re_json=True)
    if not res:
        _SPAMWATCH_CACHE[user_id] = False
        return False
    _SPAMWATCH_CACHE[user_id] = bool(res.get("id"))
    return bool(res.get("id"))


async def get_cas_banned(kst, user_id: int) -> bool:
    if user_id in _CAS_CACHE:
        return _CAS_CACHE.get(user_id)
    url = f"https://api.cas.chat/check?user_id={user_id}"
    res = await Fetch(url, re_json=True)
    if not res:
        _CAS_CACHE[user_id] = False
        return False
    _CAS_CACHE[user_id] = res.get("ok")
    return res.get("ok")


plugins_help["info"] = {
    "{i}dc": "Finds the nearest datacenter from my server.",
    "{i}sg [reply]/[in_private]/[username/mention/id]": "Get names and usernames by sangmata.",
    "{i}created [reply]/[in_private]/[username/mention/id]": "Get account creation date. Per-id is cached in 2 minutes.",
    "{i}total [reply]/[username/mention/id]": "Get total user messages.",
    "{i}stats": "Show my profile stats. Total stickers and bots is cached in 2 minutes.",
    "{i}id [reply]/[current/username]": "Get current chat/user/message id.",
    "{i}cc [reply]/[in_private]/[username/mention/id]": "Get groups in common with user.",
    "{i}info [reply]/[in_private]/[username/mention/id] [-f/full]": "Get information about user. Add '-f' to get full information including Rose Fban, SpamWatch, CAS Banned, GBanned, etc. Per-id is cached in 2 minutes.",
    "{i}chatstats [reply]/[current/username]": "Get total messages by types.",
    "{i}chatinfo [reply]/[current/username]": "Get details information about group/channel.",
}
