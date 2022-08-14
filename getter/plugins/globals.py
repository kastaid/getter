# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
import time
from contextlib import suppress
from io import BytesIO
from telethon.errors import FloodWaitError
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from . import (
    choice,
    DEVS,
    HELP,
    kasta_cmd,
    time_formatter,
    get_user,
    mentionuser,
    display_name,
    DEFAULT_GCAST_BLACKLIST,
    DEFAULT_GUCAST_BLACKLIST,
    get_blacklisted,
)


@kasta_cmd(
    pattern="gban(?: |$)(.*)",
)
@kasta_cmd(
    pattern="ggban(?: |$)(.*)",
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        await asyncio.sleep(choice((4, 6, 8)))
    msg = await kst.eor("`Gbanning...`", silent=True)
    user, reason = await get_user(kst)
    if not user:
        return await msg.eor("`Reply to some message or add their id.`", time=8)
    if user.id == kst.client.uid:
        return await msg.eor("`I can't gban myself.`", time=5)
    if user.id in DEVS:
        return await msg.eor("`I can't gban our Developers.`", time=5)
    userlink = mentionuser(user.id, display_name(user), sep="➥ ", html=True)
    success = failed = 0
    async for gg in kst.client.iter_dialogs():
        if gg.is_group or gg.is_channel:
            try:
                await kst.client.edit_permissions(gg.id, user.id, view_messages=False)
                await asyncio.sleep(0.5)
                success += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    await kst.client.edit_permissions(gg.id, user.id, view_messages=False)
                    await asyncio.sleep(0.5)
                    success += 1
                except BaseException:
                    failed += 1
            except BaseException:
                failed += 1
    with suppress(BaseException):
        await kst.client(ReportSpamRequest(user.id))
    with suppress(BaseException):
        await kst.client(BlockRequest(user.id))
    reason = reason if reason else "No Reason"
    text = (
        r"\\<b>#Gbanned</b>// {} in [<code>+{}-{}</code>] groups and channels – <b>Reason:</b> <code>{}</code>".format(
            userlink,
            success,
            failed,
            reason,
        )
    )
    await msg.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="ungban(?: |$)(.*)",
)
@kasta_cmd(
    pattern="gungban(?: |$)(.*)",
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        await asyncio.sleep(choice((4, 6, 8)))
    msg = await kst.eor("`UnGbanning...`", silent=True)
    user, _ = await get_user(kst)
    if not user:
        return await msg.eor("`Reply to some message or add their id.`", time=8)
    msg = await msg.eor("`Force UnGbanning...`")
    userlink = mentionuser(user.id, display_name(user), sep="➥ ", html=True)
    success = failed = 0
    async for gg in kst.client.iter_dialogs():
        if gg.is_group or gg.is_channel:
            try:
                await kst.client.edit_permissions(gg.id, user.id, view_messages=True)
                await asyncio.sleep(0.5)
                success += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    await kst.client.edit_permissions(gg.id, user.id, view_messages=True)
                    await asyncio.sleep(0.5)
                    success += 1
                except BaseException:
                    failed += 1
            except BaseException:
                failed += 1
    with suppress(BaseException):
        await kst.client(UnblockRequest(user.id))
    text = r"\\<b>#UnGbanned</b>// {} in [<code>+{}-{}</code>] groups and channels.".format(
        userlink,
        success,
        failed,
    )
    await msg.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="gkick(?: |$)(.*)",
)
@kasta_cmd(
    pattern="ggkick(?: |$)(.*)",
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        await asyncio.sleep(choice((4, 6, 8)))
    msg = await kst.eor("`Gkicking...`", silent=True)
    user, _ = await get_user(kst)
    if not user:
        return await msg.eor("`Reply to some message or add their id.`", time=8)
    if user.id == kst.client.uid:
        return await msg.eor("`I can't gkick myself.`", time=5)
    if user.id in DEVS:
        return await msg.eor("`I can't gkick our Developers.`", time=5)
    userlink = mentionuser(user.id, display_name(user), sep="➥ ", html=True)
    success = failed = 0
    async for gg in kst.client.iter_dialogs():
        if gg.is_group or gg.is_channel:
            try:
                await kst.client.kick_participant(gg.id, user.id)
                await asyncio.sleep(0.5)
                success += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    await kst.client.kick_participant(gg.id, user.id)
                    await asyncio.sleep(0.5)
                    success += 1
                except BaseException:
                    failed += 1
            except BaseException:
                failed += 1
    text = r"\\<b>#Gkicked</b>// {} in [<code>+{}-{}</code>] groups and channels.".format(
        userlink,
        success,
        failed,
    )
    await msg.eor(text, parse_mode="html")


@kasta_cmd(
    pattern=r"g(admin|)cast(?: |$)([\s\S]*)",
)
@kasta_cmd(
    pattern=r"gg(admin|)cast(?: |$)([\s\S]*)",
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        await asyncio.sleep(choice((4, 6, 8)))
    is_admin = True if kst.text and kst.text[2:7] == "admin" or kst.text[3:8] == "admin" else False
    match = kst.pattern_match.group(2)
    if match:
        content = match
    elif kst.is_reply:
        content = await kst.get_reply_message()
    else:
        return await kst.eod("`Give some text to Gcast or reply message.`", silent=True)
    start_time = time.time()
    msg = await kst.eor(
        "⚡ __**Gcasting to {}...**__".format(
            "groups as admin" if is_admin else "all groups",
        ),
        silent=True,
    )
    success = failed = 0
    error = ""
    GCAST_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/gcastblacklist.py",
        attempts=6,
        fallbacks=DEFAULT_GCAST_BLACKLIST,
    )
    async for gg in kst.client.iter_dialogs():
        if gg.is_group:
            chat = gg.entity.id
            if int("-100" + str(chat)) not in GCAST_BLACKLIST and (
                not is_admin or (gg.entity.admin_rights or gg.entity.creator)
            ):
                try:
                    await kst.client.send_message(chat, content)
                    await asyncio.sleep(choice((2, 3, 4, 5)))
                    success += 1
                except FloodWaitError as fw:
                    await asyncio.sleep(fw.seconds + 10)
                    try:
                        await kst.client.send_message(chat, content)
                        await asyncio.sleep(choice((2, 3, 4, 5)))
                        success += 1
                    except Exception as err:
                        error += f"• {err}\n"
                        failed += 1
                except Exception as err:
                    error += "• " + str(err) + "\n"
                    failed += 1
    taken = time_formatter((time.time() - start_time) * 1000)
    text = r"\\**#Gcast**// `{}` in [`+{}-{}`] {}.".format(
        taken,
        success,
        failed,
        "groups as admin" if is_admin else "groups",
    )
    if not error:
        with suppress(BaseException):
            with BytesIO(str.encode(error)) as file:
                file.name = "gcast_error.log"
                await kst.client.send_file(
                    kst.chat_id,
                    file=file,
                    caption=r"\\**#Getter**// `Gcast Error Logs`",
                    force_document=True,
                    allow_cache=False,
                    silent=True,
                )
    await msg.eor(text)


@kasta_cmd(
    pattern=r"gucast(?: |$)([\s\S]*)",
)
@kasta_cmd(
    pattern=r"ggucast(?: |$)([\s\S]*)",
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        await asyncio.sleep(choice((4, 6, 8)))
    match = kst.pattern_match.group(1)
    if match:
        content = match
    elif kst.is_reply:
        content = await kst.get_reply_message()
    else:
        return await kst.eod("`Give some text to Gucast or reply message.`", silent=True)
    start_time = time.time()
    msg = await kst.eor(
        "⚡ __**Gucasting in all pm users...**__",
        silent=True,
    )
    success = failed = 0
    GUCAST_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/gucastblacklist.py",
        attempts=6,
        fallbacks=DEFAULT_GUCAST_BLACKLIST,
    )
    DND = set(DEVS + GUCAST_BLACKLIST)
    async for gg in kst.client.iter_dialogs():
        if gg.is_user and not gg.entity.bot:
            chat = gg.id
            if chat not in DND:
                try:
                    await kst.client.send_message(chat, content)
                    await asyncio.sleep(choice((2, 3, 4, 5)))
                    success += 1
                except FloodWaitError as fw:
                    await asyncio.sleep(fw.seconds + 10)
                    try:
                        await kst.client.send_message(chat, content)
                        await asyncio.sleep(choice((2, 3, 4, 5)))
                        success += 1
                    except BaseException:
                        failed += 1
                except BaseException:
                    failed += 1
    taken = time_formatter((time.time() - start_time) * 1000)
    text = r"\\**#Gucast**// `{}` in [`+{}-{}`] users.".format(
        taken,
        success,
        failed,
    )
    await msg.eor(text)


HELP.update(
    {
        "globals": [
            "Globals",
            """❯ `{i}gban <reply/username/id> <reason (optional)>`
Globally Ban user (temporary) and report as spam.

❯ `{i}ungban <reply/username/id>`
Globally Unban user.

❯ `{i}gkick <reply/username/id>`
Globally Kick user (temporary).

❯ `{i}gcast <text/reply>`
Send broadcast messages to all groups.

❯ `{i}gadmincast <text/reply>`
Same as above, but only in your admin groups.

❯ `{i}gucast <text/reply>`
Send broadcast messages in all pm users.

**DWYOR ~ Do With Your Own Risk**
""",
        ]
    }
)
