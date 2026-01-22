# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import csv
from datetime import datetime
from random import choice
from time import monotonic

import aiofiles
from aiocsv import AsyncDictReader, AsyncWriter
from telethon import events
from telethon.errors import (
    ChannelPrivateError,
    FloodWaitError,
    InputUserDeactivatedError,
    UserAlreadyParticipantError,
    UserChannelsTooMuchError,
    UserKickedError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
)
from telethon.tl import functions as fun, types as typ

from . import (
    DEVS,
    INVITE_WORKER,
    NOCHATS,
    TZ,
    Root,
    get_user_status,
    get_username,
    hl,
    is_telegram_link,
    kasta_cmd,
    normalize_chat_id,
    plugins_help,
    sendlog,
    time_formatter,
)

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
done_limit_text = """
✅ <b>DONE INVITING GOT LIMIT</b>

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
done_error_text = """
⚠️ <b>DONE INVITING AN ERROR</b>

<b><u>Error</u></b>
<pre>{}</pre>

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
canceled_text = """
✅ **The process has been canceled**

**Mode:** `{}`
**Current:** `{}`
**{}:** `{}`
**Time:** `{}`
"""
_INVITING_LOCK, _SCRAPING_LOCK, _ADDING_LOCK = asyncio.Lock(), asyncio.Lock(), asyncio.Lock()


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
    ga = kst.client
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    yy = await kst.eor("`Checking...`", silent=True)
    resp = None
    bot = "SpamBot"
    await ga.unblock(bot)
    async with ga.conversation(bot) as conv:
        try:
            resp = conv.wait_event(
                events.NewMessage(
                    incoming=True,
                    from_users=conv.chat_id,
                ),
                timeout=None,
            )
            await conv.send_message("/start")
            resp = await resp
            await conv.read()
        except asyncio.exceptions.TimeoutError:
            pass
    if not resp:
        return yy.try_delete()
    await yy.eor(f"~ {resp.text}")


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
        return await kst.eor("`Please wait until previous •invite• finished...`", time=5, silent=True)
    async with _INVITING_LOCK:
        ga = kst.client
        yy = await kst.eor("`Processing...`", silent=True)
        target = await get_chat_info(kst, yy)
        if not target:
            return
        target_id = target.full_chat.id
        args = kst.pattern_match.group(1).split(" ")
        is_active = bool(
            len(args) > 1
            and args[1].lower()
            in {
                "active",
                "a",
            }
        )
        is_online = bool(
            len(args) > 1
            and args[1].lower()
            in {
                "online",
                "on",
            }
        )
        if is_active:
            filters = (
                "within_month",
                "long_time_ago",
            )
        elif is_online:
            filters = (
                "within_week",
                "within_month",
                "long_time_ago",
            )
        else:
            filters = ("none",)
        start_time = monotonic()
        local_now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        max_success, success, failed, error = 300, 0, 0, "none"
        chat = await kst.get_chat()
        INVITE_WORKER[chat_id] = {
            "mode": "invite",
            "msg_id": yy.id,
            "current": chat.title,
            "success": success,
            "now": local_now,
        }
        try:
            yy = await yy.eor("`Checking Permissions...`")
            async for x in ga.iter_participants(target_id):
                if not INVITE_WORKER.get(chat_id):
                    break
                if (
                    not (x.deleted or x.bot or x.is_self or hasattr(x.participant, "admin_rights"))
                    and get_user_status(x) not in filters
                ):
                    try:
                        if error.lower().startswith(("too many", "a wait of")) or success > max_success:
                            if INVITE_WORKER.get(chat_id):
                                INVITE_WORKER.pop(chat_id)
                            taken = time_formatter((monotonic() - start_time) * 1000)
                            try:
                                waitfor = int("".join(filter(str.isdigit, error.lower())))
                            except ValueError:
                                waitfor = 0
                            flood = time_formatter(waitfor * 1000)
                            done_limit = done_limit_text.format(
                                flood,
                                error,
                                success,
                                failed,
                                taken,
                                f"{ga.full_name} ({ga.uid})",
                                local_now,
                            )
                            await yy.eor(done_limit, parse_mode="html")
                            return await sendlog(done_limit, parse_mode="html")
                        await ga(
                            fun.channels.InviteToChannelRequest(
                                chat_id,
                                users=[x.id],
                            )
                        )
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
                        failed += 1
                    except ChannelPrivateError as err:
                        if INVITE_WORKER.get(chat_id):
                            INVITE_WORKER.pop(chat_id)
                        taken = time_formatter((monotonic() - start_time) * 1000)
                        done_error = done_error_text.format(
                            str(err),
                            success,
                            failed,
                            taken,
                            f"{ga.full_name} ({ga.uid})",
                            local_now,
                        )
                        await yy.eor(done_error, parse_mode="html")
                        return await sendlog(done_error, parse_mode="html")
                    except Exception as err:
                        error = str(err)
                        failed += 1
        except BaseException:
            pass
        if INVITE_WORKER.get(chat_id):
            INVITE_WORKER.pop(chat_id)
        taken = time_formatter((monotonic() - start_time) * 1000)
        done = done_text.format(
            success,
            failed,
            taken,
            f"{ga.full_name} ({ga.uid})",
            local_now,
        )
        await yy.eor(done, parse_mode="html")
        await sendlog(done, parse_mode="html")


@kasta_cmd(
    pattern="getmembers?(?: |$)(.*)",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    if _SCRAPING_LOCK.locked():
        return await kst.eor("`Please wait until previous •scraping• finished...`", time=5)
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
        is_append = bool(len(args) > 1 and args[1].lower() in {"-a", "a", "append"})
        start_time = monotonic()
        local_now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        members, admins, bots = 0, 0, 0
        members_file = "members_list.csv"
        admins_file = "admins_list.csv"
        bots_file = "bots_list.csv"
        await yy.eor("`Scraping Members...`")
        members_exist = bool(is_append and (Root / members_file).exists())
        if members_exist:
            with open(members_file) as f:
                rows = [int(x[0]) for x in csv.reader(f) if str(x[0]).isdecimal()]
            members = len(rows)
            async with aiofiles.open(members_file, mode="a") as f:
                writer = AsyncWriter(f, delimiter=",")
                # aggressive=True : telethon.errors.common.MultiError: ([None, None, None, FloodWaitError('A wait of 11 seconds is required (caused by GetParticipantsRequest)'),
                try:
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
                except BaseException:
                    pass
        else:
            async with aiofiles.open(members_file, mode="w") as f:
                writer = AsyncWriter(f, delimiter=",")
                await writer.writerow(["user_id", "hash", "username"])
                try:
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
                except BaseException:
                    pass
        await yy.eor("`Scraping Admins...`")
        async with aiofiles.open(admins_file, mode="w") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            try:
                async for x in ga.iter_participants(
                    target_id,
                    filter=typ.ChannelParticipantsAdmins,
                ):
                    if not (x.deleted or x.bot or x.is_self):
                        try:
                            await writer.writerow([x.id, x.access_hash, x.username])
                            admins += 1
                        except BaseException:
                            pass
            except BaseException:
                pass
        await yy.eor("`Scraping Bots...`")
        async with aiofiles.open(bots_file, mode="w") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            try:
                async for x in ga.iter_participants(
                    target_id,
                    filter=typ.ChannelParticipantsBots,
                ):
                    if not x.deleted:
                        try:
                            await writer.writerow([x.id, x.access_hash, x.username])
                            bots += 1
                        except BaseException:
                            pass
            except BaseException:
                pass
        taken = time_formatter((monotonic() - start_time) * 1000)
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
        )


@kasta_cmd(
    pattern="add(member|admin|bot)s?$",
    groups_only=True,
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    if INVITE_WORKER.get(chat_id) or _ADDING_LOCK.locked():
        return await kst.eor("`Please wait until previous •adding• finished...`", time=5)
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
        start_time = monotonic()
        local_now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        try:
            await yy.eor(f"`Reading {csv_file} file...`")
            async with aiofiles.open(csv_file) as f:
                async for row in AsyncDictReader(f, delimiter=","):
                    user = {"user_id": int(row["user_id"]), "hash": int(row["hash"])}
                    users.append(user)
        except FileNotFoundError:
            return await yy.eor(
                f"File `{csv_file}` not found.\nPlease run `{hl}getmembers [username/link/id]/[reply]` and try again!"
            )
        success = 0
        chat = await kst.get_chat()
        INVITE_WORKER[chat_id] = {
            "mode": "add",
            "msg_id": yy.id,
            "current": chat.title,
            "success": success,
            "now": local_now,
        }
        for user in users:
            if not INVITE_WORKER.get(chat_id):
                break
            if success == 50:
                await yy.eor(f"`🔄 Reached 50 members, wait until {900 / 60} minutes...`")
                await asyncio.sleep(900)
            try:
                adding = typ.InputPeerUser(user["user_id"], user["hash"])
                await ga(
                    fun.channels.InviteToChannelRequest(
                        chat_id,
                        users=[adding],
                    )
                )
                success += 1
                INVITE_WORKER[chat_id].update({"success": success})
                await yy.eor(f"`Adding {success} {mode}...`")
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    adding = typ.InputPeerUser(user["user_id"], user["hash"])
                    await ga(
                        fun.channels.InviteToChannelRequest(
                            chat_id,
                            users=[adding],
                        )
                    )
                    success += 1
                    INVITE_WORKER[chat_id].update({"success": success})
                    await yy.eor(f"`Adding {success} {mode}...`")
                except ChannelPrivateError:
                    break
                except BaseException:
                    pass
            except ChannelPrivateError:
                break
            except BaseException:
                pass
        if INVITE_WORKER.get(chat_id):
            INVITE_WORKER.pop(chat_id)
        taken = time_formatter((monotonic() - start_time) * 1000)
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
    worker = INVITE_WORKER.get(chat_id)
    if INVITE_WORKER.get(chat_id):
        INVITE_WORKER.pop(chat_id)
    await kst.sod(
        canceled_text.format(
            worker.get("mode"),
            worker.get("current"),
            "Inviting" if worker.get("mode") == "invite" else "Adding",
            worker.get("success"),
            worker.get("now"),
        ),
        silent=True,
        time=100,
        reply_to=worker.get("msg_id"),
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
