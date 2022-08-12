# getter < httpsl://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
import datetime
import time
from contextlib import suppress
from csv import reader as csv_read
from aiocsv import AsyncDictReader, AsyncWriter
from aiofiles import open as aiopen
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
    UserKickedError,
    UserChannelsTooMuchError,
    YouBlockedUserError,
)
from telethon.tl.functions.channels import GetFullChannelRequest, InviteToChannelRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    InputPeerUser,
    UserStatusEmpty,
    UserStatusLastMonth,
)
from . import (
    choice,
    Root,
    HELP,
    WORKER,
    DEVS,
    NOCHATS,
    events,
    TZ,
    hl,
    kasta_cmd,
    display_name,
    get_username,
    is_telegram_link,
    time_formatter,
)

INVITING_LOCK = asyncio.Lock()
SCRAPING_LOCK = asyncio.Lock()
ADDING_LOCK = asyncio.Lock()
spamb = "@SpamBot"

with_error_text = """
✅ <b>DONE INVITING WITH ERROR</b>
(<code>MAY GOT LIMIT ERROR AND TRY AGAIN LATER</code>)

<b>✘ Error Message:</b>
<pre>{}</pre>

• <b>Invited:</b> <code>{}</code>
• <b>Failed:</b> <code>{}</code>
• <b>Taken:</b> <code>{}</code>

<b>User:</b> <code>{}</code>
<b>LocalTime:</b> <code>{}</code>
"""

invite_text = """
🔄 <b>INVITING...</b>

• <b>Invited:</b> <code>{}</code>
• <b>Failed:</b> <code>{}</code>

<b>✘ Last Error:</b> <code>{}</code>
"""

done_text = """
✅ <b>DONE INVITING</b>

• <b>Invited:</b> <code>{}</code>
• <b>Failed:</b> <code>{}</code>
• <b>Taken:</b> <code>{}</code>

<b>User:</b> <code>{}</code>
<b>LocalTime:</b> <code>{}</code>
"""

getmembers_text = """
✅ Scraping {} completed in <code>{}</code>

<b>ID:</b> <code>{}</code>
<b>Title:</b> <code>{}</code>
<b>Username:</b> {}
<b>Total:</b> <code>{}</code>
<b>Done ({}):</b> <code>{}</code>
<b>LocalTime:</b> <code>{}</code>
"""

no_process_text = "`There is no running proccess.`"
cancel_text = "`Requested to cancel the current process...`"
cancelled_text = """
✅ **The process has been cancelled**

**Mode:** `{}`
**Current:** `{}`
**{}:** `{}`
**LocalTime:** `{}`
"""


async def get_groupinfo(kst, msg, group=1):
    info = None
    args = kst.pattern_match.group(group).split(" ")
    target = args[0]
    if not target:
        await msg.eod("`Required Username/Link/ID as target.`")
        return None
    if str(target).isdecimal() or (str(target).startswith("-") and str(target)[1:].isdecimal()):
        if str(target).startswith("-100"):
            target = int(str(target).replace("-100", ""))
        elif str(target).startswith("-"):
            target = int(str(target).replace("-", ""))
        else:
            target = int(target)
    if isinstance(target, str):
        if is_telegram_link(target):
            target = get_username(target)
    try:
        info = await kst.client(GetFullChatRequest(chat_id=target))
    except BaseException:
        try:
            info = await kst.client(GetFullChannelRequest(channel=target))
        except ValueError:
            await msg.eod("`You must join the target.`")
            return None
        except BaseException:
            await msg.eod("`Invalid Username/Link/ID as target, please re-check.`")
            return None
    return info


async def limit(kst, conv):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=conv.chat_id))
        await conv.send_message("/start")
        resp = await resp
        await resp.mark_read(clear_mentions=True)
        # await kst.client(telethon.tl.functions.messages.DeleteHistoryRequest(conv.chat_id, max_id=0, just_clear=False, revoke=False))
        return resp.message.message
    except YouBlockedUserError:
        await kst.client(UnblockRequest(spamb))
        return await limit(kst, conv)


@kasta_cmd(
    pattern="limit$",
    edited=True,
    no_crash=True,
    blacklist_chats=True,
    chats=NOCHATS,
)
@kasta_cmd(
    pattern="glimit$",
    own=True,
    senders=DEVS,
)
async def _(kst):
    if not kst.out:
        await asyncio.sleep(choice((4, 6, 8)))
    msg = await kst.eor("`Checking...`", silent=True)
    async with kst.client.conversation(spamb) as conv:
        resp = await limit(kst, conv)
        await msg.eor(f"```{resp}```")


@kasta_cmd(
    pattern="inviteall(?: |$)(.*)",
    groups_only=True,
)
@kasta_cmd(
    pattern="ginvite(?: |$)(.*)",
    groups_only=True,
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs and kst.client.uid in DEVS:
        return
    if is_devs:
        await asyncio.sleep(choice((4, 6, 8)))
    if WORKER.get(kst.chat_id) or INVITING_LOCK.locked():
        await kst.eor("`Please wait until previous INVITE finished...`", time=5, silent=True)
        return
    async with INVITING_LOCK:
        msg = await kst.eor("`Processing...`", silent=True)
        group = await get_groupinfo(kst, msg)
        if not group:
            return
        start_time = time.time()
        local_now = datetime.datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
        me = await kst.client.get_me()
        success = failed = 0
        max_success = 300
        error = "None"
        WORKER[kst.chat_id] = {
            "mode": "invite",
            "current": kst.chat.title,
            "success": success,
            "now": local_now,
        }
        try:
            await msg.eor("`Checking Permissions...`")
            async for x in kst.client.iter_participants(group.full_chat.id):
                if not WORKER.get(kst.chat_id):
                    await msg.try_delete()
                    return
                if not (
                    x.deleted or x.bot or x.is_self or isinstance(x.participant, ChannelParticipantsAdmins)
                ) and not isinstance(x.status, (UserStatusLastMonth, UserStatusEmpty)):
                    try:
                        if error.lower().startswith(("too many", "a wait of")) or success > max_success:
                            if WORKER.get(kst.chat_id):
                                WORKER.pop(kst.chat_id)
                            taken = time_formatter((time.time() - start_time) * 1000)
                            await msg.eor(
                                with_error_text.format(
                                    error,
                                    success,
                                    failed,
                                    taken,
                                    f"{display_name(me)} ({me.id})",
                                    local_now,
                                ),
                                parse_mode="html",
                            )
                            return
                        await kst.client(InviteToChannelRequest(channel=kst.chat_id, users=[x.id]))
                        success += 1
                        WORKER[kst.chat_id].update({"success": success})
                        await msg.eor(
                            invite_text.format(
                                success,
                                failed,
                                error,
                            ),
                            parse_mode="html",
                        )
                    except (
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
        except BaseException:  # TypeError
            pass
        with suppress(BaseException):
            if WORKER.get(kst.chat_id):
                WORKER.pop(kst.chat_id)
        taken = time_formatter((time.time() - start_time) * 1000)
        await msg.eor(
            done_text.format(
                success,
                failed,
                taken,
                f"{display_name(me)} ({me.id})",
                local_now,
            ),
            parse_mode="html",
        )
        return


@kasta_cmd(
    pattern="getmembers?(?: |$)(.*)",
)
async def _(kst):
    if SCRAPING_LOCK.locked():
        await kst.eor("`Please wait until previous SCRAPING finished...`", time=5)
        return
    async with SCRAPING_LOCK:
        msg = await kst.eor("`Processing...`")
        group = await get_groupinfo(kst, msg)
        if not group:
            return
        if kst.chat_id == int("-100" + str(group.full_chat.id)):
            return await msg.try_delete()
        args = kst.pattern_match.group(1).split(" ")
        is_append = True if len(args) > 1 and args[1].lower() in ("append", "a") else False
        start_time = time.time()
        local_now = datetime.datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
        members = admins = bots = 0
        members_file = "members_list.csv"
        admins_file = "admins_list.csv"
        bots_file = "bots_list.csv"
        await msg.eor("`Scraping Members...`")
        members_exist = True if is_append and (Root / members_file).exists() else False
        if members_exist:
            rows = [int(x[0]) for x in csv_read(open(members_file, "r")) if str(x[0]).isdecimal()]
            members = len(rows)
            async with aiopen(members_file, mode="a") as f:
                writer = AsyncWriter(f, delimiter=",")
                # aggressive=True : telethon.errors.common.MultiError: ([None, None, None, FloodWaitError('A wait of 11 seconds is required (caused by GetParticipantsRequest)'),
                try:
                    async for x in kst.client.iter_participants(group.full_chat.id):
                        if not (
                            x.deleted or x.bot or x.is_self or isinstance(x.participant, ChannelParticipantsAdmins)
                        ) and not isinstance(x.status, (UserStatusLastMonth, UserStatusEmpty)):
                            try:
                                if x.id not in rows:
                                    await writer.writerow([x.id, x.access_hash, x.username])
                                    members += 1
                            except BaseException:
                                pass
                except BaseException:
                    pass
        else:
            async with aiopen(members_file, mode="w") as f:
                writer = AsyncWriter(f, delimiter=",")
                await writer.writerow(["user_id", "hash", "username"])
                try:
                    async for x in kst.client.iter_participants(group.full_chat.id):
                        if not (
                            x.deleted or x.bot or x.is_self or isinstance(x.participant, ChannelParticipantsAdmins)
                        ) and not isinstance(x.status, (UserStatusLastMonth, UserStatusEmpty)):
                            try:
                                await writer.writerow([x.id, x.access_hash, x.username])
                                members += 1
                            except BaseException:
                                pass
                except BaseException:
                    pass
        await msg.eor("`Scraping Admins...`")
        async with aiopen(admins_file, mode="w") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            async for x in kst.client.iter_participants(group.full_chat.id, filter=ChannelParticipantsAdmins):
                if not (x.deleted or x.bot or x.is_self):
                    try:
                        await writer.writerow([x.id, x.access_hash, x.username])
                        admins += 1
                    except BaseException:
                        pass
        await msg.eor("`Scraping Bots...`")
        async with aiopen(bots_file, mode="w") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            async for x in kst.client.iter_participants(group.full_chat.id, filter=ChannelParticipantsBots):
                if not x.deleted:
                    try:
                        await writer.writerow([x.id, x.access_hash, x.username])
                        bots += 1
                    except BaseException:
                        pass
        taken = time_formatter((time.time() - start_time) * 1000)
        await msg.eor("`Uploading CSV Files...`")
        await kst.client.send_file(
            kst.chat_id,
            file=members_file,
            caption=getmembers_text.format(
                "Members",
                taken,
                group.full_chat.id,
                group.chats[0].title,
                "@" + group.chats[0].username if group.chats[0].username else "None",
                group.full_chat.participants_count,
                "exclude self, bots, admins, deleted accounts, status last month, status empty",
                members,
                local_now,
            ),
            parse_mode="html",
            force_document=True,
            allow_cache=False,
        )
        await kst.client.send_file(
            kst.chat_id,
            file=admins_file,
            caption=getmembers_text.format(
                "Admins",
                taken,
                group.full_chat.id,
                group.chats[0].title,
                "@" + group.chats[0].username if group.chats[0].username else "None",
                group.full_chat.participants_count,
                "exclude self, bots, deleted accounts",
                admins,
                local_now,
            ),
            parse_mode="html",
            force_document=True,
            allow_cache=False,
        )
        await kst.client.send_file(
            kst.chat_id,
            file=bots_file,
            caption=getmembers_text.format(
                "Bots",
                taken,
                group.full_chat.id,
                group.chats[0].title,
                "@" + group.chats[0].username if group.chats[0].username else "None",
                group.full_chat.participants_count,
                "exclude deleted bots",
                bots,
                local_now,
            ),
            parse_mode="html",
            force_document=True,
            allow_cache=False,
        )
        await msg.try_delete()
        return


@kasta_cmd(
    pattern="add(member|admin|bot)s?$",
    groups_only=True,
)
async def _(kst):
    if WORKER.get(kst.chat_id) or ADDING_LOCK.locked():
        await kst.eor("`Please wait until previous ADDING finished...`", time=5)
        return
    async with ADDING_LOCK:
        msg = await kst.eor("`Processing...`")
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
        local_now = datetime.datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
        try:
            await msg.eor(f"`Reading {csv_file} file...`")
            async with aiopen(csv_file, mode="r") as f:
                async for row in AsyncDictReader(f, delimiter=","):
                    user = {"user_id": int(row["user_id"]), "hash": int(row["hash"])}
                    users.append(user)
        except FileNotFoundError:
            await msg.eor(
                f"File `{csv_file}` not found.\nPlease run `{hl}getmembers <username/link/id (group as target)>` and try again!",
                time=15,
            )
            return
        success = 0
        WORKER[kst.chat_id] = {
            "mode": "add",
            "current": kst.chat.title,
            "success": success,
            "now": local_now,
        }
        for user in users:
            if not WORKER.get(kst.chat_id):
                await msg.try_delete()
                return
            if success == 30:
                await msg.eor(f"`🔄 Reached 30 members, wait until {900/60} minutes...`")
                await asyncio.sleep(900)
            try:
                adding = InputPeerUser(user["user_id"], user["hash"])
                await kst.client(InviteToChannelRequest(channel=kst.chat_id, users=[adding]))
                success += 1
                WORKER[kst.chat_id].update({"success": success})
                await msg.eor(f"`Adding {success} {mode}...`")
                await asyncio.sleep(choice((4, 5, 6)))
            except BaseException:
                pass
        with suppress(BaseException):
            if WORKER.get(kst.chat_id):
                WORKER.pop(kst.chat_id)
        taken = time_formatter((time.time() - start_time) * 1000)
        await msg.eor(f"`✅ Completed adding {success} {mode} in {taken}` at `{local_now}`")


@kasta_cmd(
    pattern="cancel$",
    groups_only=True,
)
@kasta_cmd(
    pattern="gcancel$",
    groups_only=True,
    own=True,
    senders=DEVS,
)
async def _(kst):
    if not kst.out:
        await asyncio.sleep(choice((4, 6, 8)))
    if not WORKER.get(kst.chat_id):
        return await kst.eod(no_process_text, silent=True)
    msg = await kst.eor(cancel_text, silent=True)
    _worker = WORKER.get(kst.chat_id)
    with suppress(BaseException):
        if WORKER.get(kst.chat_id):
            WORKER.pop(kst.chat_id)
    await msg.eor(
        cancelled_text.format(
            _worker["mode"],
            _worker["current"],
            "Inviting" if _worker["mode"] == "invite" else "Adding",
            _worker["success"],
            _worker["now"],
        ),
        time=100,
    )


HELP.update(
    {
        "core": [
            "Core",
            """❯ `{i}inviteall <username/link/id (as target)>`
Invite people's (exclude self, bots, admins, deleted accounts, status last month, status empty) to your current group/channel.

❯ `{i}getmembers <username/link/id (as target)>`
Scraping members from the group and then save as csv files (members, admins, bots).
Run this command in everywhere exclude the target groups.

**Note:**
- You must join the target if you use id, for two commands above.
- Do not delete running messages if you have running process or the process will be stopped and users can't join.
- Telethon (Telegram APIs) have a limit to scraping members. If you need to get more members use this command with options <`append`> or <`a`> example: `<{i}getmembers @username append`>. Repeat it after finished to get more members without duplicated rows. You can also combination with difference groups!
- Files members_list.csv, admins_list.csv and bot_list.csv saved at main directory and not removed, will replaced if you run the command above again. But if the app restarted files will be destroyed, so keep downloading latest files.

❯ `{i}addmembers|{i}addadmins|{i}addbots`
Adding members to your current group/channel from saved csv files generate by command above as members or admins or bots (there's a limit).

❯ `{i}cancel`
Cancel the running process, both for invite and add.

❯ `{i}limit`
Check your account was limit or not.

**DWYOR ~ Do With Your Own Risk**
""",
        ]
    }
)
