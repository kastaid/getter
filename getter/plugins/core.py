# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import csv
import datetime
import time
import aiofiles
from aiocsv import AsyncDictReader, AsyncWriter
from telethon.errors.rpcerrorlist import (
    FloodWaitError,
    InputUserDeactivatedError,
    UserAlreadyParticipantError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
    UserKickedError,
    UserChannelsTooMuchError,
    YouBlockedUserError,
)
from telethon.tl import functions as fun, types as typ
from . import (
    Root,
    INVITE_WORKER,
    DEVS,
    NOCHATS,
    tz,
    hl,
    kasta_cmd,
    plugins_help,
    events,
    suppress,
    choice,
    is_telegram_link,
    get_username,
    get_user_status,
    normalize_chat_id,
    time_formatter,
)

with_error_text = """
✅ <b>DONE INVITING WITH ERROR</b>

<b><u>Note</u></b>
<pre>Got limit error and try again after {}</pre>

<b><u>Error</u></b>
<pre>{}</pre>

• <b>Invited:</b> <code>{}</code>
• <b>Failed:</b> <code>{}</code>
• <b>Taken:</b> <code>{}</code>

<b>User:</b> <code>{}</code>
<b>Time:</b> <code>{}</code>
"""
invite_text = """
🔄 <b>INVITING...</b>

• <b>Invited:</b> <code>{}</code>
• <b>Failed:</b> <code>{}</code>

<b>Last Error:</b> <code>{}</code>
"""
done_text = """
✅ <b>DONE INVITING</b>

• <b>Invited:</b> <code>{}</code>
• <b>Failed:</b> <code>{}</code>
• <b>Taken:</b> <code>{}</code>

<b>User:</b> <code>{}</code>
<b>Time:</b> <code>{}</code>
"""
getmembers_text = """
✅ Scraping {} completed in <code>{}</code>

<b>ID:</b> <code>{}</code>
<b>Title:</b> <code>{}</code>
<b>Username:</b> {}
<b>Total:</b> <code>{}</code>
<b>Done ({}):</b> <code>{}</code>
<b>Time:</b> <code>{}</code>
"""
no_process_text = "`There is no running proccess.`"
cancelled_text = """
✅ **The process has been cancelled**

**Mode:** `{}`
**Current:** `{}`
**{}:** `{}`
**Time:** `{}`
"""
_INVITING_LOCK = asyncio.Lock()
_SCRAPING_LOCK = asyncio.Lock()
_ADDING_LOCK = asyncio.Lock()


@kasta_cmd(
    pattern="limit$",
    edited=True,
    no_chats=True,
    chats=NOCHATS,
)
@kasta_cmd(
    pattern="glimit$",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    yy = await kst.eor("`Checking...`", silent=True)
    resp = None
    async with kst.client.conversation("SpamBot") as conv:
        resp = await conv_limit(conv)
    if not resp:
        return yy.try_delete()
    await yy.eor(f"~ {resp.text}")
    await resp.try_delete()


@kasta_cmd(
    pattern="inviteall(?: |$)(.*)",
    groups_only=True,
)
@kasta_cmd(
    pattern="ginvite(?: |$)(.*)",
    groups_only=True,
    dev=True,
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    if kst.is_dev:
        if kst.client.uid in DEVS:
            return
        await asyncio.sleep(choice((4, 6, 8)))
    if INVITE_WORKER.get(chat_id) or _INVITING_LOCK.locked():
        await kst.eor("`Please wait until previous •invite• finished...`", time=5, silent=True)
        return
    async with _INVITING_LOCK:
        ga = kst.client
        yy = await kst.eor("`Processing...`", silent=True)
        target = await get_chat_info(kst, yy)
        if not target:
            return
        target_id = target.full_chat.id
        start_time = time.time()
        local_now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        max_success, success, failed, error = 300, 0, 0, "none"
        INVITE_WORKER[chat_id] = {
            "mode": "invite",
            "msg_id": yy.id,
            "current": kst.chat.title,
            "success": success,
            "now": local_now,
        }
        try:
            await yy.eor("`Checking Permissions...`")
            async for x in ga.iter_participants(target_id):
                if not INVITE_WORKER.get(chat_id):
                    break
                if (
                    not (x.deleted or x.bot or x.is_self or hasattr(x.participant, "admin_rights"))
                    and get_user_status(x) != "long_time_ago"
                ):
                    try:
                        if error.lower().startswith(("too many", "a wait of")) or success > max_success:
                            if INVITE_WORKER.get(chat_id):
                                INVITE_WORKER.pop(chat_id)
                            taken = time_formatter((time.time() - start_time) * 1000)
                            try:
                                waitfor = int("".join(filter(str.isdigit, error.lower())))
                            except ValueError:
                                waitfor = 0
                            flood = time_formatter(waitfor * 1000)
                            await yy.eor(
                                with_error_text.format(
                                    flood,
                                    error,
                                    success,
                                    failed,
                                    taken,
                                    f"{ga.full_name} ({ga.uid})",
                                    local_now,
                                ),
                                parse_mode="html",
                            )
                            return
                        await ga(fun.channels.InviteToChannelRequest(chat_id, users=[x.id]))
                        success += 1
                        INVITE_WORKER[chat_id].update({"success": success})
                        await yy.eor(
                            invite_text.format(
                                success,
                                failed,
                                error,
                            ),
                            parse_mode="html",
                        )
                    except (
                        InputUserDeactivatedError,
                        UserAlreadyParticipantError,
                        UserNotMutualContactError,
                        UserPrivacyRestrictedError,
                        UserKickedError,
                        UserChannelsTooMuchError,
                    ):
                        pass
                    except Exception as err:
                        error = str(err)
                        failed += 1
        except BaseException:
            pass
        if INVITE_WORKER.get(chat_id):
            INVITE_WORKER.pop(chat_id)
        taken = time_formatter((time.time() - start_time) * 1000)
        await yy.eor(
            done_text.format(
                success,
                failed,
                taken,
                f"{ga.full_name} ({ga.uid})",
                local_now,
            ),
            parse_mode="html",
        )


@kasta_cmd(
    pattern="getmembers?(?: |$)(.*)",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    if _SCRAPING_LOCK.locked():
        await kst.eor("`Please wait until previous •scraping• finished...`", time=5)
        return
    async with _SCRAPING_LOCK:
        ga = kst.client
        yy = await kst.eor("`Processing...`")
        target = await get_chat_info(kst, yy)
        if not target:
            return
        target_id = target.full_chat.id
        if chat_id == target_id:
            return await yy.try_delete()
        args = kst.pattern_match.group(1).split(" ")
        is_append = bool(len(args) > 1 and args[1].lower() in ("-a", "a", "append"))
        start_time = time.time()
        local_now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        members, admins, bots = 0, 0, 0
        members_file = "members_list.csv"
        admins_file = "admins_list.csv"
        bots_file = "bots_list.csv"
        await yy.eor("`Scraping Members...`")
        members_exist = bool(is_append and (Root / members_file).exists())
        if members_exist:
            with open(members_file, "r") as f:
                rows = [int(x[0]) for x in csv.reader(f) if str(x[0]).isdecimal()]
            members = len(rows)
            async with aiofiles.open(members_file, mode="a") as f:
                writer = AsyncWriter(f, delimiter=",")
                # aggressive=True : telethon.errors.common.MultiError: ([None, None, None, FloodWaitError('A wait of 11 seconds is required (caused by GetParticipantsRequest)'),
                with suppress(BaseException):
                    async for x in ga.iter_participants(target_id):
                        if (
                            not (x.deleted or x.bot or x.is_self or hasattr(x.participant, "admin_rights"))
                            and get_user_status(x) != "long_time_ago"
                            and x.id not in rows
                        ):
                            try:
                                await writer.writerow([x.id, x.access_hash, x.username])
                                members += 1
                            except BaseException:
                                pass
        else:
            async with aiofiles.open(members_file, mode="w") as f:
                writer = AsyncWriter(f, delimiter=",")
                await writer.writerow(["user_id", "hash", "username"])
                with suppress(BaseException):
                    async for x in ga.iter_participants(target_id):
                        if (
                            not (x.deleted or x.bot or x.is_self or hasattr(x.participant, "admin_rights"))
                            and get_user_status(x) != "long_time_ago"
                        ):
                            try:
                                await writer.writerow([x.id, x.access_hash, x.username])
                                members += 1
                            except BaseException:
                                pass
        await yy.eor("`Scraping Admins...`")
        async with aiofiles.open(admins_file, mode="w") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            with suppress(BaseException):
                async for x in ga.iter_participants(target_id, filter=typ.ChannelParticipantsAdmins):
                    if not (x.deleted or x.bot or x.is_self):
                        try:
                            await writer.writerow([x.id, x.access_hash, x.username])
                            admins += 1
                        except BaseException:
                            pass
        await yy.eor("`Scraping Bots...`")
        async with aiofiles.open(bots_file, mode="w") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            with suppress(BaseException):
                async for x in ga.iter_participants(target_id, filter=typ.ChannelParticipantsBots):
                    if not x.deleted:
                        try:
                            await writer.writerow([x.id, x.access_hash, x.username])
                            bots += 1
                        except BaseException:
                            pass
        taken = time_formatter((time.time() - start_time) * 1000)
        await yy.eor("`Uploading CSV Files...`")
        await yy.eor(
            getmembers_text.format(
                "Members",
                taken,
                target_id,
                target.chats[0].title,
                "@" + target.chats[0].username if target.chats[0].username else "none",
                target.full_chat.participants_count,
                "exclude self, bots, admins, deleted accounts, status long_time_ago",
                members,
                local_now,
            ),
            file=members_file,
            parse_mode="html",
            force_document=True,
            allow_cache=False,
        )
        await yy.eor(
            getmembers_text.format(
                "Admins",
                taken,
                target_id,
                target.chats[0].title,
                "@" + target.chats[0].username if target.chats[0].username else "none",
                target.full_chat.participants_count,
                "exclude self, bots, deleted accounts",
                admins,
                local_now,
            ),
            file=admins_file,
            parse_mode="html",
            force_document=True,
            allow_cache=False,
        )
        await yy.eor(
            getmembers_text.format(
                "Bots",
                taken,
                target_id,
                target.chats[0].title,
                "@" + target.chats[0].username if target.chats[0].username else "none",
                target.full_chat.participants_count,
                "exclude deleted bots",
                bots,
                local_now,
            ),
            file=bots_file,
            parse_mode="html",
            force_document=True,
            allow_cache=False,
        )


@kasta_cmd(
    pattern="add(member|admin|bot)s?$",
    groups_only=True,
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    if INVITE_WORKER.get(chat_id) or _ADDING_LOCK.locked():
        await kst.eor("`Please wait until previous •adding• finished...`", time=5)
        return
    async with _ADDING_LOCK:
        ga = kst.client
        yy = await kst.eor("`Processing...`")
        users = []
        mode = None
        args = kst.pattern_match.group(1).lower()
        if args.startswith("member"):
            mode = "members"
        elif args.startswith("admin"):
            mode = "admins"
        elif args.startswith("bot"):
            mode = "bots"
        csv_file = mode + "_list.csv"
        start_time = time.time()
        local_now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        try:
            await yy.eor(f"`Reading {csv_file} file...`")
            async with aiofiles.open(csv_file, mode="r") as f:
                async for row in AsyncDictReader(f, delimiter=","):
                    user = {"user_id": int(row["user_id"]), "hash": int(row["hash"])}
                    users.append(user)
        except FileNotFoundError:
            await yy.eor(
                f"File `{csv_file}` not found.\nPlease run `{hl}getmembers [username/link/id]/[reply]` and try again!"
            )
            return
        success = 0
        INVITE_WORKER[chat_id] = {
            "mode": "add",
            "msg_id": yy.id,
            "current": kst.chat.title,
            "success": success,
            "now": local_now,
        }
        for user in users:
            if not INVITE_WORKER.get(chat_id):
                break
            if success == 50:
                await yy.eor(f"`🔄 Reached 50 members, wait until {900/60} minutes...`")
                await asyncio.sleep(900)
            try:
                adding = typ.InputPeerUser(user["user_id"], user["hash"])
                await ga(fun.channels.InviteToChannelRequest(chat_id, users=[adding]))
                success += 1
                INVITE_WORKER[chat_id].update({"success": success})
                await yy.eor(f"`Adding {success} {mode}...`")
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    adding = typ.InputPeerUser(user["user_id"], user["hash"])
                    await ga(fun.channels.InviteToChannelRequest(chat_id, users=[adding]))
                    success += 1
                    INVITE_WORKER[chat_id].update({"success": success})
                    await yy.eor(f"`Adding {success} {mode}...`")
                except BaseException:
                    pass
            except BaseException:
                pass
        if INVITE_WORKER.get(chat_id):
            INVITE_WORKER.pop(chat_id)
        taken = time_formatter((time.time() - start_time) * 1000)
        await yy.eor(f"`✅ Completed adding {success} {mode} in {taken}` at `{local_now}`")


@kasta_cmd(
    pattern="cancel$",
    groups_only=True,
)
@kasta_cmd(
    pattern="gcancel$",
    groups_only=True,
    dev=True,
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    if kst.is_dev:
        if kst.client.uid in DEVS:
            return
        await asyncio.sleep(choice((4, 6, 8)))
    if not INVITE_WORKER.get(chat_id):
        return await kst.eod(no_process_text, silent=True)
    _worker = INVITE_WORKER.get(chat_id)
    if INVITE_WORKER.get(chat_id):
        INVITE_WORKER.pop(chat_id)
    await kst.sod(
        cancelled_text.format(
            _worker.get("mode"),
            _worker.get("current"),
            "Inviting" if _worker.get("mode") == "invite" else "Adding",
            _worker.get("success"),
            _worker.get("now"),
        ),
        silent=True,
        time=100,
        reply_to=_worker.get("msg_id"),
    )


async def get_chat_info(kst, yy, group=1):
    info = None
    target = await kst.client.get_text(kst, group=group)
    if not target:
        await yy.eod("`Required username/link/id as target.`")
        return None
    target = target.split(" ")[0]
    target = normalize_chat_id(target)
    if isinstance(target, str) and is_telegram_link(target):
        target = get_username(target)
    try:
        info = await kst.client(fun.messages.GetFullChatRequest(target))
    except BaseException:
        try:
            info = await kst.client(fun.channels.GetFullChannelRequest(target))
        except ValueError:
            await yy.eod("`You must join the target.`")
            return None
        except BaseException:
            await yy.eod("`Invalid username/link/id as target, please re-check.`")
            return None
    return info


async def conv_limit(conv):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        yy = await conv.send_message("/start")
        resp = await resp
        await yy.try_delete()
        await conv.read(clear_mentions=True, clear_reactions=True)
        return resp
    except asyncio.exceptions.TimeoutError:
        return None
    except YouBlockedUserError:
        await conv._client.unblock(conv.chat_id)
        return await conv_limit(conv)


plugins_help["core"] = {
    "{i}inviteall [username/link/id]/[reply]": "Invite people's (exclude self, bots, admins, deleted accounts, status long_time_ago) to current group/channel.",
    "{i}getmembers [username/link/id]/[reply] [append/a]": """Scraping members from the group and then save as csv files (members, admins, bots).
Run this command in everywhere exclude the target groups.

**Note:**
- You must join the target if you use id, for two commands above.
- Do not delete running messages if you have running process or the process will be stopped and users can't join.
- Telethon (Telegram APIs) have a limit to scraping members. If you need to get more members use this command with options 'append' or 'a' example: <`{i}getmembers @username append`>. Repeat it after finished to get more members without duplicated rows. You can also combination with difference groups!
- Files members_list.csv, admins_list.csv and bot_list.csv saved at main directory and not removed, will replaced if you run the command above again. But if the app restarted files will be destroyed, so keep downloading latest files.""",
    "{i}addmembers|{i}addadmins|{i}addbots": "Adding members to current group/channel from saved csv files generate by command above as members or admins or bots (there's a limit).",
    "{i}cancel": "Cancel the running process, both for invite and add.",
    "{i}limit": """Check my account limit or not.

**DWYOR ~ Do With Your Own Risk**""",
}
