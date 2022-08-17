# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from contextlib import suppress
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from . import (
    choice,
    DEVS,
    HELP,
    hl,
    kasta_cmd,
    display_name,
    get_user,
)


@kasta_cmd(
    pattern="(read|r)$|([rR])$",
    edited=True,
    no_crash=True,
)
async def _(kst):
    await kst.try_delete()
    await kst.mark_read(clear_mentions=True, clear_reactions=True)


@kasta_cmd(
    pattern="(del|d)$|([d](el)?)$",
    ignore_case=True,
    edited=True,
    no_crash=True,
)
async def _(kst):
    await kst.try_delete()
    if kst.is_reply:
        await (await kst.get_reply_message()).try_delete()


@kasta_cmd(
    pattern="purge$",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    total = 0
    chat = await kst.get_input_chat()
    rep = await kst.get_reply_message()
    async for msg in kst.client.iter_messages(
        chat,
        min_id=kst.reply_to_msg_id or 0,
    ):
        await msg.try_delete()
        total += 1
        await asyncio.sleep(0.2)
    await rep.try_delete()
    await kst.sod(f"`Purged {total}`", time=5, silent=True)


@kasta_cmd(
    pattern="purgeme(?: |$)(.*)",
    no_crash=True,
)
@kasta_cmd(
    pattern="gpurgeme(?: |$)(.*)",
    own=True,
    senders=DEVS,
    no_crash=True,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        await asyncio.sleep(choice((1, 2, 3)))
    num = kst.pattern_match.group(1)
    if num and not kst.is_reply:
        total = 0
        limit = int(num) if num.isdecimal() else None
        async for msg in kst.client.iter_messages(
            kst.chat_id,
            limit=limit,
            from_user="me",
        ):
            await msg.try_delete()
            total += 1
        if total >= 2:
            await kst.eor(f"`Purged {total}`", time=5, silent=True)
        return
    if not (num or kst.is_reply):
        await kst.eod(f"Reply message to purge from or use like `{hl}purgeme <number>`")
        return
    total = 0
    chat = await kst.get_input_chat()
    async for msg in kst.client.iter_messages(
        chat,
        from_user="me",
        min_id=kst.reply_to_msg_id or 0,
    ):
        await msg.try_delete()
        total += 1
    await kst.eor(f"`Purged {total}`", time=5, silent=True)


@kasta_cmd(
    pattern="purgeall$",
    func=lambda e: e.is_reply,
    no_crash=True,
)
async def _(kst):
    total = 0
    chat = await kst.get_input_chat()
    from_user = (await kst.get_reply_message()).sender_id
    user = await kst.client.get_entity(from_user)
    async for msg in kst.client.iter_messages(
        chat,
        from_user=from_user,
    ):
        await msg.try_delete()
        total += 1
        await asyncio.sleep(0.2)
    await kst.sod(f"`Purged {total} messages from {display_name(user)}`", time=5, silent=True)


@kasta_cmd(
    pattern="copy$",
    no_crash=True,
    func=lambda e: e.is_reply,
)
async def _(kst):
    await kst.try_delete()
    copy = await kst.get_reply_message()
    return await copy.reply(copy)


@kasta_cmd(
    pattern="(send|dm)(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    if len(kst.text.split()) <= 1:
        return await kst.eor("`Give chat username or id where to send.`", time=5)
    chat = kst.text.split()[1]
    try:
        with suppress(ValueError):
            chat = int(chat)
        chat_id = await kst.client.get_peer_id(chat)
    except Exception as err:
        return await kst.eor(f"**ERROR:**\n`{err}`")
    if len(kst.text.split()) > 2:
        msg = kst.text.split(maxsplit=2)[2]
    elif kst.reply_to:
        msg = await kst.get_reply_message()
    else:
        return await kst.eor("`Give text to send or reply to message.`", time=5)
    try:
        _ = await kst.client.send_message(chat_id, msg)
        delivered = "Message Delivered!"
        if not _.is_private:
            delivered = f"[Message Delivered!]({_.message_link})"
        await kst.eor(delivered)
    except Exception as err:
        await kst.eor(f"**ERROR:**\n`{err}`")


@kasta_cmd(
    pattern="(f|)saved$",
    no_crash=True,
    func=lambda e: e.is_reply,
)
async def _(kst):
    rep = await kst.get_reply_message()
    if kst.pattern_match.group(1).strip() == "f":
        await rep.forward_to(kst.sender_id)
    else:
        await kst.client.send_message(kst.sender_id, rep)
    await kst.eor("`saved`", time=5)


@kasta_cmd(
    pattern="ids?$",
    no_crash=True,
)
async def _(kst):
    chat_id = kst.chat_id or kst.from_id
    if kst.is_reply:
        reply = await kst.get_reply_message()
        user_id, msg_id = (reply.sender_id, reply.id)
        text = (
            f"├ **User ID:** `{user_id}`"
            if kst.is_private
            else f"├ **Chat ID:** `{chat_id}`\n├ **User ID:** `{user_id}`"
        )
        text = text + f"\n└ **Message ID:** `{msg_id}`"
    else:
        text = "├ **User ID:** " if kst.is_private else "├ **Chat ID:** "
        text = f"{text}`{chat_id}`" + f"\n└ **Message ID:** `{kst.id}`"
    await kst.eor(text, time=100)


@kasta_cmd(
    pattern="(delayspam|ds)(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    try:
        args = kst.text.split(" ", 3)
        delay = float(args[1])
        count = int(args[2])
        msg = str(args[3])
    except BaseException:
        return await kst.eor(f"`{hl}delayspam <time/in seconds> <count> <text>`", time=10)
    await kst.try_delete()
    try:
        delay = 2 if delay and int(delay) < 2 else delay
        for _ in range(count):
            await kst.respond(msg)
            await asyncio.sleep(delay)
    except BaseException:
        pass


@kasta_cmd(
    pattern="block(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Blocking...`", silent=True)
    user, _ = await get_user(kst)
    if not user:
        return await msg.eor("`Reply to some message or add their id.`", time=8)
    if user.id == kst.client.uid:
        return await msg.eor("`I can't block myself.`", time=5)
    if user.id in DEVS:
        return await msg.eor("`I can't block our Developers.`", time=5)
    with suppress(BaseException):
        await kst.client(ReportSpamRequest(user.id))
    try:
        await kst.client(BlockRequest(user.id))
        text = "**User has been blocked!**"
    except BaseException:
        text = "**User can't blocked!**"
    await msg.eor(text)


@kasta_cmd(
    pattern="unblock(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`UnBlocking...`", silent=True)
    user, _ = await get_user(kst)
    if not user:
        return await msg.eor("`Reply to some message or add their id.`", time=8)
    try:
        await kst.client(UnblockRequest(user.id))
        text = "**User has been unblocked!**"
    except BaseException:
        text = "**User can't unblocked!**"
    await msg.eor(text)


@kasta_cmd(
    pattern="kickme$",
    no_crash=True,
    groups_only=True,
)
async def _(kst):
    await kst.try_delete()
    with suppress(BaseException):
        await kst.client(LeaveChannelRequest(channel=kst.chat_id))


HELP.update(
    {
        "chats": [
            "Chats",
            """❯ `{i}read|{i}r|r|R`
Marks messages as read in current chat also clear mentions and reactions.

❯ `{i}del|{i}d|d|D|del|Del`
Delete the replied message.

❯ `{i}purge <reply>`
Purge all messages from the replied message.

❯ `{i}purgeme <reply>`
Purge only your messages from the replied message.

❯ `{i}purgeall <reply>`
Delete all messages of replied user.

❯ `{i}copy <reply>`
Copy the replied message.

❯ `{i}send|{i}dm <username/id> <text/reply>`
Send message to User/Chat.

❯ `{i}saved <reply>`
Save that replied message to Saved Messages.

❯ `{i}fsaved <reply>`
Forward that replied message to Saved Messages.

❯ `{i}id|{i}ids`
Get current Chat/User/Message ID.

❯ `{i}delayspam|{i}ds <time/in seconds> <count> <text>`
Spam chat with delays in seconds (min 2 seconds).

❯ `{i}block <reply/username>`
Block mentioned user.

❯ `{i}unblock <reply/username>`
Unblock mentioned user.

❯ `{i}kickme`
Leaves the group.
""",
        ]
    }
)
