# getter < httpsl://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from asyncio import Lock, sleep
from contextlib import suppress
from csv import reader as csv_read
from datetime import datetime, timezone
from secrets import choice
from time import time
from aiocsv import AsyncDictReader, AsyncWriter
from aiofiles import open as aiopen
from telethon.errors import (
    UserAlreadyParticipantError,
    UserNotMutualContactError,
    UserPrivacyRestrictedError,
    UserKickedError,
    UserChannelsTooMuchError,
    YouBlockedUserError,
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest as InviteUser
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import ChannelParticipantsAdmins as Admins
from telethon.tl.types import ChannelParticipantsBots as Bots
from telethon.tl.types import InputPeerUser
from telethon.tl.types import UserStatusEmpty as StatusEmpty
from telethon.tl.types import UserStatusLastMonth as LastMonth
from . import (
    StartTime,
    __version__,
    Root,
    HELP,
    WORKER,
    DEVS,
    NOCHATS,
    Var,
    events,
    TZ,
    hl,
    kasta_cmd,
    display_name,
    get_username,
    is_telegram_link,
    time_formatter,
)

INVITING_LOCK = Lock()
SCRAPING_LOCK = Lock()
ADDING_LOCK = Lock()
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
❎ **The process has been cancelled**

**Mode:** `{}`
**Current:** `{}`
**{}:** `{}`
**LocalTime:** `{}`
"""

test_text = """
<b>ID:</b> <code>{}</code>
<b>Heroku App:</b> <code>{}</code>
<b>Getter Version:</b> <code>{}</code>
<b>Uptime:</b> <code>{}</code>
<b>UTC Now:</b> <code>{}</code>
"""


async def limit(e, conv):
    try:
        resp = conv.wait_event(events.NewMessage(incoming=True, from_users=178220800))
        await conv.send_message("/start")
        resp = await resp
        await e.client.send_read_acknowledge(conv.chat_id)
        return resp.message.message
    except YouBlockedUserError:
        await e.client(UnblockRequest(spamb))
        return await limit(e, conv)


@kasta_cmd(blacklist_chats=True, chats=NOCHATS, pattern="limit$")
@kasta_cmd(own=True, senders=DEVS, pattern="glimit$")
async def _(e):
    if not (hasattr(e, "out") and e.out):
        await sleep(choice((4, 6, 8)))
    with suppress(BaseException):
        Kst = await e.eor("`Checking...`", silent=True)
        async with e.client.conversation(spamb) as conv:
            resp = await limit(e, conv)
            await Kst.eor("~ " + resp)


async def get_groupinfo(e, m, group=1):
    info = None
    args = e.pattern_match.group(group).split(" ")
    target = args[0]
    if not target:
        await m.eod("`Required Username/Link/ID as target.`")
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
        info = await e.client(GetFullChatRequest(chat_id=target))
    except BaseException:
        try:
            info = await e.client(GetFullChannelRequest(channel=target))
        except ValueError:
            await m.eod("`You must join the target.`")
            return None
        except BaseException:
            await m.eod("`Invalid Username/Link/ID as target, please re-check.`")
            return None
    return info


@kasta_cmd(
    func=lambda x: not x.is_private,
    pattern="inviteall(?: |$)(.*)",
)
@kasta_cmd(
    func=lambda x: not x.is_private,
    own=True,
    senders=DEVS,
    pattern="ginvite(?: |$)(.*)",
)
async def _(e):
    is_devs = True if not (hasattr(e, "out") and e.out) else False
    if is_devs and e.client.uid in DEVS:
        return
    if is_devs:
        await sleep(choice((4, 6, 8)))
    if WORKER.get(e.chat_id) or INVITING_LOCK.locked():
        await e.eor("`Please wait until previous INVITE finished...`", time=5, silent=True)
        return
    async with INVITING_LOCK:
        Kst = await e.eor("`Processing...`", silent=True)
        group = await get_groupinfo(e, Kst)
        if not group:
            return
        start_time = time()
        local_now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
        me = await e.client.get_me()
        success = failed = 0
        max_success = 150
        error = "None"
        chat = await e.get_chat()
        WORKER[e.chat_id] = {
            "mode": "invite",
            "current": chat.title,
            "success": success,
            "now": local_now,
        }
        try:
            await Kst.eor("`Checking Permissions...`")
            async for x in e.client.iter_participants(group.full_chat.id):
                if not WORKER.get(e.chat_id):
                    await Kst.try_delete()
                    return
                if not (x.deleted or x.bot or x.is_self or isinstance(x.participant, Admins)) and not isinstance(
                    x.status, (LastMonth, StatusEmpty)
                ):
                    try:
                        if error.startswith(("Too many", "A wait")) or success > max_success:
                            taken = time_formatter((time() - start_time) * 1000)
                            await Kst.eor(
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
                        await e.client(InviteUser(channel=chat, users=[x.id]))
                        success += 1
                        WORKER[e.chat_id].update({"success": success})
                        await Kst.eor(
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
            if WORKER.get(e.chat_id):
                WORKER.pop(e.chat_id)
        taken = time_formatter((time() - start_time) * 1000)
        await Kst.eor(
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


@kasta_cmd(pattern="getmembers?(?: |$)(.*)")
async def _(e):
    if SCRAPING_LOCK.locked():
        await e.eor("`Please wait until previous SCRAPING finished...`", time=5, silent=True)
        return
    async with SCRAPING_LOCK:
        Kst = await e.eor("`Processing...`", silent=True)
        group = await get_groupinfo(e, Kst)
        if not group:
            return
        if e.chat_id == int("-100" + str(group.full_chat.id)):
            return await Kst.try_delete()
        args = e.pattern_match.group(1).split(" ")
        is_append = True if len(args) > 1 and args[1].lower() in ["append", "a"] else False
        start_time = time()
        local_now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
        members = admins = bots = 0
        members_file = "members_list.csv"
        admins_file = "admins_list.csv"
        bots_file = "bots_list.csv"
        await Kst.eor("`Scraping Members...`")
        members_exist = True if is_append and (Root / members_file).exists() else False
        if members_exist:
            rows = [int(x[0]) for x in csv_read(open(members_file, "r", encoding="utf-8")) if str(x[0]).isdecimal()]
            members = len(rows)
            async with aiopen(file=members_file, mode="a", encoding="utf-8") as f:
                writer = AsyncWriter(f, delimiter=",")
                # aggressive=True : telethon.errors.common.MultiError: ([None, None, None, FloodWaitError('A wait of 11 seconds is required (caused by GetParticipantsRequest)'),
                try:
                    async for x in e.client.iter_participants(group.full_chat.id):
                        if not (
                            x.deleted or x.bot or x.is_self or isinstance(x.participant, Admins)
                        ) and not isinstance(x.status, (LastMonth, StatusEmpty)):
                            try:
                                if x.id not in rows:
                                    await writer.writerow([x.id, x.access_hash, x.username])
                                    members += 1
                            except BaseException:
                                pass
                except BaseException:
                    pass
        else:
            async with aiopen(file=members_file, mode="w", encoding="utf-8") as f:
                writer = AsyncWriter(f, delimiter=",")
                await writer.writerow(["user_id", "hash", "username"])
                try:
                    async for x in e.client.iter_participants(group.full_chat.id):
                        if not (
                            x.deleted or x.bot or x.is_self or isinstance(x.participant, Admins)
                        ) and not isinstance(x.status, (LastMonth, StatusEmpty)):
                            try:
                                await writer.writerow([x.id, x.access_hash, x.username])
                                members += 1
                            except BaseException:
                                pass
                except BaseException:
                    pass
        await Kst.eor("`Scraping Admins...`")
        async with aiopen(file=admins_file, mode="w", encoding="utf-8") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            async for x in e.client.iter_participants(group.full_chat.id, filter=Admins):
                if not (x.deleted or x.bot or x.is_self):
                    try:
                        await writer.writerow([x.id, x.access_hash, x.username])
                        admins += 1
                    except BaseException:
                        pass
        await Kst.eor("`Scraping Bots...`")
        async with aiopen(file=bots_file, mode="w", encoding="utf-8") as f:
            writer = AsyncWriter(f, delimiter=",")
            await writer.writerow(["user_id", "hash", "username"])
            async for x in e.client.iter_participants(group.full_chat.id, filter=Bots):
                if not x.deleted:
                    try:
                        await writer.writerow([x.id, x.access_hash, x.username])
                        bots += 1
                    except BaseException:
                        pass
        taken = time_formatter((time() - start_time) * 1000)
        await Kst.eor("`Uploading CSV Files...`")
        await e.client.send_file(
            e.chat_id,
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
        await e.client.send_file(
            e.chat_id,
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
        await e.client.send_file(
            e.chat_id,
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
        await Kst.try_delete()
        return


@kasta_cmd(func=lambda x: not x.is_private, pattern="add(member|admin|bot)s?$")
async def _(e):
    if WORKER.get(e.chat_id) or ADDING_LOCK.locked():
        await e.eor("`Please wait until previous ADDING finished...`", time=5, silent=True)
        return
    async with ADDING_LOCK:
        Kst = await e.eor("`Processing...`", silent=True)
        users = []
        mode = None
        args = e.pattern_match.group(1).lower()
        if args.startswith("member"):
            mode = "members"
        elif args.startswith("admin"):
            mode = "admins"
        elif args.startswith("bot"):
            mode = "bots"
        csv_file = mode + "_list.csv"
        start_time = time()
        local_now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
        chat = await e.get_chat()
        try:
            await Kst.eor(f"`Reading {csv_file} file...`")
            async with aiopen(file=csv_file, mode="r", encoding="utf-8") as f:
                async for row in AsyncDictReader(f, delimiter=","):
                    user = {"user_id": int(row["user_id"]), "hash": int(row["hash"])}
                    users.append(user)
        except FileNotFoundError:
            await Kst.eor(
                f"File `{csv_file}` not found.\nPlease run `{hl}getmembers <username/link/id (group as target)>` and try again!",
                time=15,
            )
            return
        success = 0
        WORKER[e.chat_id] = {
            "mode": "add",
            "current": chat.title,
            "success": success,
            "now": local_now,
        }
        for user in users:
            if not WORKER.get(e.chat_id):
                await Kst.try_delete()
                return
            if success == 30:
                await Kst.eor(f"`🔄 Reached 30 members, wait until {900/60} minutes...`")
                await sleep(900)
            try:
                adding = InputPeerUser(user["user_id"], user["hash"])
                await e.client(InviteUser(channel=chat, users=[adding]))
                success += 1
                WORKER[e.chat_id].update({"success": success})
                await Kst.eor(f"`Adding {success} {mode}...`")
                await sleep(choice((4, 5, 6)))
            except BaseException:
                pass
        with suppress(BaseException):
            if WORKER.get(e.chat_id):
                WORKER.pop(e.chat_id)
        taken = time_formatter((time() - start_time) * 1000)
        await Kst.eor(f"`✅ Completed adding {success} {mode} in {taken}` at `{local_now}`")


@kasta_cmd(
    func=lambda x: not x.is_private,
    pattern="cancel$",
)
@kasta_cmd(
    func=lambda x: not x.is_private,
    own=True,
    senders=DEVS,
    pattern="gcancel$",
)
async def _(e):
    if not (hasattr(e, "out") and e.out):
        await sleep(choice((4, 6, 8)))
    if not WORKER.get(e.chat_id):
        return await e.eod(no_process_text, silent=True)
    Kst = await e.eor(cancel_text, silent=True)
    _worker = WORKER.get(e.chat_id)
    with suppress(BaseException):
        if WORKER.get(e.chat_id):
            WORKER.pop(e.chat_id)
    await Kst.eor(
        cancelled_text.format(
            _worker["mode"],
            _worker["current"],
            "Inviting" if _worker["mode"] == "invite" else "Adding",
            _worker["success"],
            _worker["now"],
        )
    )


@kasta_cmd(pattern="test")
@kasta_cmd(own=True, senders=DEVS, pattern="gtest(?: |$)(.*)")
async def _(e):
    is_devs = True if not (hasattr(e, "out") and e.out) else False
    clean = False
    if is_devs:
        opt = e.pattern_match.group(1)
        if opt:
            user_id = version = None
            try:
                user_id = int(opt)
            except ValueError:
                version = opt
            if not version and user_id != e.client.uid:
                return
            if not user_id and version == __version__:
                return
            clean = True
        if not clean:
            await sleep(choice((4, 6, 8)))
    # http://www.timebie.com/std/utc
    utc_now = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
    uptime = time_formatter((time() - StartTime) * 1000)
    Kst = test_text.format(
        e.client.uid,
        Var.HEROKU_APP_NAME or "None",
        __version__,
        uptime,
        utc_now,
    )
    await e.eor(
        Kst,
        parse_mode="html",
        force_reply=True,
        silent=True,
        time=15 if clean else 0,
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

**DWYOR ~ Do With Your Own Risk!**
""",
        ]
    }
)
