# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from asyncio import sleep
from asyncio.exceptions import TimeoutError as AsyncTimeout
from contextlib import suppress
from secrets import choice
from telethon.errors import YouBlockedUserError
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import Chat
from . import (
    DEVS,
    HELP,
    display_name,
    get_user,
    hl,
    kasta_cmd,
    parse_pre,
)


@kasta_cmd(disable_errors=True, pattern="del|(d|D|del|Del)")
async def _(e):
    if hasattr(e, "text") and e.text.lower() not in [f"{hl}del", "d", "del"]:
        return
    await e.try_delete()
    reply = await e.get_reply_message()
    if reply:
        await reply.try_delete()


@kasta_cmd(disable_errors=True, pattern="purge(?: |$)(.*)")
async def _(e):
    match = e.pattern_match.group(1)
    if not e.is_reply:
        return await e.try_delete()
    if match or e.is_private or isinstance(e.chat, Chat):
        count = 0
        num = int(match) if match.isdecimal() else None
        async for m in e.client.iter_messages(
            e.chat_id,
            limit=num,
            min_id=e.reply_to_msg_id or None,
        ):
            await m.try_delete()
            count += 1
            await sleep(0.3)
        await e.eor(f"`Purged {count}`", time=2, silent=True)
        return
    with suppress(BaseException):
        msgs = [x for x in range(e.reply_to_msg_id, e.id + 1)]  # noqa: C416
        await e.client.delete_messages(e.chat_id, msgs)
    Kst = await e.client.send_message(e.chat_id, "`purged`", silent=True)
    await sleep(2)
    await Kst.try_delete()


@kasta_cmd(disable_errors=True, pattern="purgeme(?: |$)(.*)")
@kasta_cmd(disable_errors=True, own=True, senders=DEVS, pattern="gpurgeme(?: |$)(.*)")
async def _(e):
    match = e.pattern_match.group(1)
    count = 0
    if not (hasattr(e, "out") and e.out):
        await sleep(choice((1, 2, 3)))
    if match and not e.is_reply:
        num = int(match) if match.isdecimal() else None
        async for m in e.client.iter_messages(e.chat_id, limit=num, from_user="me"):
            await m.try_delete()
            count += 1
        if count >= 2:
            await e.eor(f"`Purged {count}`", time=2, silent=True)
        return
    if not (match or e.is_reply):
        await e.eor(f"Reply to a message to purge from or use it like `{hl}purgeme <num>`", time=10)
        return
    chat = await e.get_input_chat()
    msgs = []
    async for m in e.client.iter_messages(
        chat,
        from_user="me",
        min_id=e.reply_to_msg_id or None,
    ):
        msgs.append(m)
        count += 1
        msgs.append(e.reply_to_msg_id)
        if len(msgs) == 100:
            await e.client.delete_messages(chat, msgs)
            msgs = []
    if msgs:
        await e.client.delete_messages(chat, msgs)
    if count >= 2:
        await e.eor(f"`Purged {count}`", time=2, silent=True)


@kasta_cmd(disable_errors=True, pattern="ids?")
async def _(e):
    chat_id = e.chat_id or e.from_id
    if e.is_reply:
        reply = await e.get_reply_message()
        userid = reply.sender_id
        text = f"**User ID:** `{userid}`" if e.is_private else f"**Chat ID:** `{chat_id}`\n**User ID:** `{userid}`"
        text = text + f"\n**Message ID:** `{reply.id}`"
        await e.eor(text)
        return
    text = "**User ID:** " if e.is_private else "**Chat ID:** "
    text = f"{text}`{chat_id}`" + f"\n**Message ID:** `{e.id}`"
    await e.eor(text, silent=True)


@kasta_cmd(disable_errors=True, pattern="total(?: |$)(.*)")
async def _(e):
    match = e.pattern_match.group(1)
    if match:
        user = match
    elif e.is_reply:
        user = (await e.get_reply_message()).sender_id
    else:
        user = "me"
    msg = await e.client.get_messages(e.chat_id, 0, from_user=user)
    user = await e.client.get_entity(user)
    await e.eor(f"Total messages from `{display_name(user)}` [`{msg.total}`]")


@kasta_cmd(disable_errors=True, pattern="(delayspam|ds)(?: |$)(.*)")
async def _(e):
    try:
        args = e.text.split(" ", 3)
        delay = float(args[1])
        count = int(args[2])
        msg = str(args[3])
    except BaseException:
        return await e.eor(f"**Usage:** `{hl}delayspam <time> <count> <text>`", time=10)
    await e.try_delete()
    try:
        delay = 5 if delay and int(delay) < 5 else delay
        for _ in range(count):
            await e.respond(msg)
            await sleep(delay)
    except Exception as err:
        await e.respond(f"**Error:** `{err}`")


@kasta_cmd(func=lambda x: not x.is_private, pattern="kickme$")
async def _(e):
    with suppress(BaseException):
        await e.try_delete()
        await e.client(LeaveChannelRequest(e.chat_id))


@kasta_cmd(disable_errors=True, pattern="sg(u)?(?: |$)(.*)")
async def _(e):
    Kst = await e.eor("`Getting...`")
    user, _ = await get_user(e, 2)
    if not user:
        await Kst.eor("`Failed, required Username/ID or reply message.`", time=15)
        return
    sangmata = "@SangMataInfo_bot"
    async with e.client.conversation(sangmata) as conv:
        try:
            await conv.send_message(f"/search_id {user.id}")
        except YouBlockedUserError:
            await e.client(UnblockRequest(sangmata))
            await conv.send_message(f"/search_id {user.id}")
        resp = []
        while True:
            try:
                res = await conv.get_response(timeout=5)
            except AsyncTimeout:
                await Kst.try_delete()
                break
            resp.append(res.text)
        await e.client.send_read_acknowledge(conv.chat_id)
    if not resp:
        await Kst.eod("`Can't fetch results.`")
    if "No records found" in resp:
        await Kst.eod("`Doesn't have any record.`")
    names, usernames = await sangmata_sep(resp)
    uname = e.pattern_match.group(1)
    msg = None
    check = usernames if uname == "u" else names
    for x in check:
        if msg:
            await e.eos(x, force_reply=True, parse_mode=parse_pre)
        else:
            msg = True
            await Kst.eor(x, parse_mode=parse_pre)


async def sangmata_sep(sglist):
    for x in sglist:
        if x.startswith("🔗"):
            sglist.remove(x)
    s = 0
    for x in sglist:
        if x.startswith("Username History"):
            break
        s += 1
    usernames = sglist[s:]
    names = sglist[:s]
    return names, usernames


HELP.update(
    {
        "chats": [
            "Chats",
            """❯ `{i}del|d|D|del|Del`
Delete a messages.

❯ `{i}purge <limit (optional)> <reply>`
Purge all messages from the replied message.

❯ `{i}purgeme <reply>`
Purge only your messages from the replied message.

❯ `{i}id|{i}ids`
Get current Chat/User/Message ID.

❯ `{i}total <username/reply>`
Get total user messages.

❯ `{i}sg <reply/username/id>`
Get names by sangmata.

❯ `{i}sgu <reply/username/id>`
Get usernames by sangmata.

❯ `{i}delayspam|{i}ds <time> <count> <text>`
Spam chat with delays in seconds (min 5 seconds).

❯ `{i}kickme`
Leaves the groups.
""",
        ]
    }
)
