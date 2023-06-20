# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
from telethon.errors.rpcerrorlist import UserBotError, FloodWaitError
from telethon.tl import functions as fun, types as typ
from . import (
    DEVS,
    hl,
    kasta_cmd,
    plugins_help,
    choice,
    formatx_send,
    display_name,
    mentionuser,
    normalize_chat_id,
    NOCHATS,
    BOTLOGS,
    DS_TASK,
    DS1_TASK,
    DS2_TASK,
    DS3_TASK,
    DS4_TASK,
)


@kasta_cmd(
    pattern="(read|r)$",  # (read|r)$|([rR])$
    edited=True,
)
async def _(kst):
    try:
        await kst.delete()
    except BaseException:
        pass
    await kst.read(
        clear_mentions=True,
        clear_reactions=True,
    )


@kasta_cmd(
    pattern="(del|d)$|([d](el)?)$",
    ignore_case=True,
    edited=True,
)
async def _(kst):
    try:
        await kst.delete()
    except BaseException:
        pass
    if kst.is_reply:
        try:
            await (await kst.get_reply_message()).delete()
        except BaseException:
            pass


@kasta_cmd(
    pattern="(purge|pg)$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    total = 0
    chat = await kst.get_input_chat()
    async for msg in kst.client.iter_messages(
        chat,
        min_id=kst.reply_to_msg_id,
    ):
        await msg.delete()
        total += 1
    try:
        await (await kst.get_reply_message()).delete()
    except BaseException:
        pass
    await kst.sod(f"`Purged {total}`", time=3, silent=True)


@kasta_cmd(
    pattern="(purgeme|pgm)(?: |$)(.*)",
)
@kasta_cmd(
    pattern="(purgeme|pgm)(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="(gpurgeme|gpgm)(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((1, 2, 3)))
    ga = kst.client
    chat = await kst.get_input_chat()
    num = kst.pattern_match.group(2)
    if kst.is_reply:
        msgs = []
        reply = await kst.get_reply_message()
        async for msg in ga.iter_messages(
            chat,
            from_user="me",
            min_id=reply.id,
        ):
            msgs.append(msg.id)
        if reply.sender_id == ga.uid:
            msgs.append(reply.id)
        if msgs:
            await ga.delete_messages(chat, msgs)
        if kst.is_dev or kst.is_sudo:
            return
        await kst.sod(f"`Purged {len(msgs)}`", time=3, silent=True)
    elif num and num.isdecimal():
        total = 0
        async for msg in ga.iter_messages(
            chat,
            from_user="me",
            limit=int(num),
        ):
            await msg.delete()
            total += 1
        if kst.is_dev or kst.is_sudo:
            return
        await kst.sod(f"`Purged {total}`", time=3, silent=True)
    else:
        await kst.eod(f"Reply my message to purgeme or use like `{hl}purgeme [number]`")


@kasta_cmd(
    pattern="purgeall$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    total = 0
    ga = kst.client
    chat = await kst.get_input_chat()
    from_user = (await kst.get_reply_message()).sender_id
    whois = display_name(await ga.get_entity(from_user))
    async for msg in ga.iter_messages(
        chat,
        from_user=from_user,
    ):
        await msg.delete()
        total += 1
    await kst.sod(f"`Purged {total} messages from {whois}`", time=3, silent=True)


@kasta_cmd(
    pattern="copy$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    try:
        await kst.delete()
    except BaseException:
        pass
    try:
        copy = await kst.get_reply_message()
        await copy.reply(copy)
    except BaseException:
        pass


@kasta_cmd(
    pattern="nodrafts?$",
)
async def _(kst):
    ga = kst.client
    drafts = 0
    yy = await kst.eor("`Processing...`")
    async for x in ga.iter_drafts():
        try:
            await x.delete()
            drafts += 1
        except BaseException:
            pass
    if not drafts:
        return await yy.eor("`no drafts found`", time=3)
    await yy.eod(f"`cleared {drafts} drafts`")


@kasta_cmd(
    pattern="sd(m|)(?: |$)(\\d*)(?: |$)((?s).*)",
)
async def _(kst):
    group = kst.pattern_match.group
    text = await kst.client.get_text(kst, group=3, plain=False)
    if not text:
        return await kst.try_delete()
    ttl = int(group(2).strip() or 1)
    if group(1).strip() == "m":
        text += f"\n\n`self-destruct message in {ttl} seconds`"
    await kst.eor(text, time=ttl)


@kasta_cmd(
    pattern="(send|dm)(?: |$)((?s).*)",
)
async def _(kst):
    ga = kst.client
    if len(kst.text.split()) <= 1:
        await kst.eor("`Give chat username or id where to send.`", time=5)
        return
    chat = kst.text.split()[1]
    try:
        chat_id = await ga.get_id(chat)
    except Exception as err:
        return await kst.eor(formatx_send(err), parse_mode="html")
    if len(kst.text.split()) > 2:
        message = kst.text.split(maxsplit=2)[2]
    elif kst.is_reply:
        message = await kst.get_reply_message()
    else:
        await kst.eor("`Give text to send or reply to message.`", time=5)
        return
    try:
        sent = await ga.send_message(chat_id, message=message)
        delivered = "Message Delivered!"
        if not sent.is_private:
            delivered = f"[{delivered}]({sent.msg_link})"
        await kst.eor(delivered)
    except Exception as err:
        await kst.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="(f|)saved(l|)$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    ga = kst.client
    group = kst.pattern_match.group
    reply = await kst.get_reply_message()
    where = (BOTLOGS if group(2).strip() == "l" else ga.uid) or ga.uid
    if group(1).strip() == "f":
        await reply.forward_to(where)
    else:
        await ga.send_message(where, reply)
    await kst.eor("`saved`", time=5)


@kasta_cmd(
    pattern="react$",
    func=lambda e: e.is_reply,
)
async def _(kst):
    yy = await kst.eor("`Reaction...`")
    reaction = choice(("👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏"))  # fmt: skip
    try:
        await (await kst.get_reply_message()).send_react(big=True, reaction=reaction)
        return await yy.eor(f"`reacted {reaction}`", time=3)
    except BaseException:
        pass
    await yy.eor("`no react`", time=3)


@kasta_cmd(
    pattern="ds(1|2|3|4|)(?: |$)((?s).*)",
)
async def _(kst):
    ga = kst.client
    chat_id = normalize_chat_id(kst.chat_id)
    ds = kst.pattern_match.group(1).strip()
    text = "Please wait until previous •ds{}• finished..."
    if (
        (ds == "1" and chat_id in DS1_TASK)
        or (ds == "2" and chat_id in DS2_TASK)
        or (ds == "3" and chat_id in DS3_TASK)
        or (ds == "4" and chat_id in DS4_TASK)
    ):
        return await kst.eor(text.format(ds), time=3)
    else:
        if chat_id in DS_TASK:
            return await kst.eor(text.format(ds), time=3)
    if kst.is_reply:
        try:
            args = kst.text.split(" ", 2)
            dly = float(args[1])
            count = int(args[2])
            message = await kst.get_reply_message()
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [seconds] [count] [reply]`", time=5)
    else:
        try:
            args = kst.text.split(" ", 3)
            dly = float(args[1])
            count = int(args[2])
            message = str(args[3])
        except BaseException:
            return await kst.eor(f"`{hl}ds{ds} [seconds] [count] [text]`", time=5)
    dly = 2 if dly and int(dly) < 2 else dly
    await ga.mute_chat(chat_id)
    await kst.try_delete()
    if ds == "1":
        DS1_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS1_TASK:
                break
            try:
                await kst.read(
                    clear_mentions=True,
                    clear_reactions=True,
                )
            except BaseException:
                pass
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except BaseException:
                break
        DS1_TASK.discard(chat_id)
    elif ds == "2":
        DS2_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS2_TASK:
                break
            try:
                await kst.read(
                    clear_mentions=True,
                    clear_reactions=True,
                )
            except BaseException:
                pass
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except BaseException:
                break
        DS2_TASK.discard(chat_id)
    elif ds == "3":
        DS3_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS3_TASK:
                break
            try:
                await kst.read(
                    clear_mentions=True,
                    clear_reactions=True,
                )
            except BaseException:
                pass
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except BaseException:
                break
        DS3_TASK.discard(chat_id)
    elif ds == "4":
        DS4_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS4_TASK:
                break
            try:
                await kst.read(
                    clear_mentions=True,
                    clear_reactions=True,
                )
            except BaseException:
                pass
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except BaseException:
                break
        DS4_TASK.discard(chat_id)
    else:
        DS_TASK.add(chat_id)
        for _ in range(count):
            if chat_id not in DS_TASK:
                break
            try:
                await kst.read(
                    clear_mentions=True,
                    clear_reactions=True,
                )
            except BaseException:
                pass
            try:
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                await ga.send_message(
                    chat_id,
                    message=message,
                    parse_mode=None,
                    link_preview=False,
                    silent=True,
                )
                await asyncio.sleep(dly)
            except BaseException:
                break
        DS_TASK.discard(chat_id)


@kasta_cmd(
    pattern="ds(1|2|3|4|)cancel$",
)
async def _(kst):
    chat_id = normalize_chat_id(kst.chat_id)
    ds = kst.pattern_match.group(1).strip()
    yy = await kst.eor("`Processing...`")
    text = "__No current •ds{}• are running.__"
    if ds == "1":
        if chat_id not in DS1_TASK:
            return await yy.eod(text.format(ds))
        DS1_TASK.discard(chat_id)
    elif ds == "2":
        if chat_id not in DS2_TASK:
            return await yy.eod(text.format(ds))
        DS2_TASK.discard(chat_id)
    elif ds == "3":
        if chat_id not in DS3_TASK:
            return await yy.eod(text.format(ds))
        DS3_TASK.discard(chat_id)
    elif ds == "4":
        if chat_id not in DS3_TASK:
            return await yy.eod(text.format(ds))
        DS4_TASK.discard(chat_id)
    else:
        if chat_id not in DS_TASK:
            return await yy.eod(text.format(ds))
        DS_TASK.discard(chat_id)
    await yy.eor("`cancelled`", time=3)


@kasta_cmd(
    pattern="report_spam(?: |$)(.*)",
)
@kasta_cmd(
    pattern="report_spam(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="greport_spam(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Reporting...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot report to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to report our awesome developers.`", time=3)
    is_reported = False
    try:
        if kst.is_private:
            # https://stackoverflow.com/a/57327383
            is_reported = await ga(
                fun.account.ReportPeerRequest(
                    user.id,
                    reason=typ.InputReportReasonSpam(),
                    message="Sends spam messages to my account. I ask Telegram to ban such user.",
                    # in many chats, we request
                )
            )
        elif kst.is_group and kst.is_reply:
            is_reported = await ga(
                fun.channels.ReportSpamRequest(
                    chat_id,
                    participant=user.id,
                    id=[kst.reply_to_msg_id],
                )
            )
        else:
            is_reported = await ga.report_spam(user.id)
    except BaseException:
        pass
    await yy.eor(
        "User {} {} reported!".format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            "was" if is_reported else "not",
        ),
        parse_mode="html",
    )


@kasta_cmd(
    pattern="invite(?: |$)(.*)",
    groups_only=True,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Processing...`")
    users = kst.pattern_match.group(1)
    if not kst.is_channel and kst.is_group:
        for x in users.split(" "):
            try:
                await ga(
                    fun.messages.AddChatUserRequest(
                        chat_id,
                        user_id=await ga.get_id(x),
                        fwd_limit=1000000,
                    ),
                )
                await yy.eor(f"Successfully invited `{x}` to `{chat_id}`")
            except Exception as err:
                await yy.eor(formatx_send(err), parse_mode="html")
    else:
        for x in users.split(" "):
            try:
                await ga(
                    fun.channels.InviteToChannelRequest(
                        chat_id,
                        users=[await ga.get_id(x)],
                    ),
                )
                await yy.eor(f"Successfully invited `{x}` to `{chat_id}`")
            except UserBotError:
                await yy.eod("`Bots can only be added as admins in channel.`")
            except Exception as err:
                await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="kickme(?: |$)(.*)",
    no_chats=True,
    chats=NOCHATS,
)
@kasta_cmd(
    pattern="gkickme(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    ga = kst.client
    chat_id = await ga.get_chat_id(kst)
    is_current = chat_id == normalize_chat_id(kst.chat_id)
    if is_current and kst.is_private:
        return await kst.eod("`Use this in for group/channel.`")
    if is_current:
        await kst.try_delete()
    try:
        await ga.kick_participant(chat_id, "me")
        if not is_current:
            await kst.eod(f"`Leave from {chat_id}.`")
    except BaseException:
        await kst.eod(f"`Cannot leave from {chat_id}, try leave manually :(`")


@kasta_cmd(
    pattern="(un|)archive(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    is_unarchive = kst.pattern_match.group(1).strip() == "un"
    chat_id = await ga.get_chat_id(kst, group=2)
    is_current = chat_id == normalize_chat_id(kst.chat_id)
    if is_current and kst.is_private:
        return await kst.eod("`Use this in for group/channel.`")
    if is_current:
        await kst.try_delete()
    if is_unarchive:
        has_unarchive = await ga.unarchive(chat_id)
        if not (has_unarchive is None):
            text = "UnArchived!"
        else:
            text = "Cannot UnArchive!"
    else:
        has_archive = await ga.archive(chat_id)
        if not (has_archive is None):
            text = "Archived!"
        else:
            text = "Cannot Archive!"
    await kst.eod(f"`{chat_id} {text}`")


@kasta_cmd(
    pattern="delchannel(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    chat_id = await ga.get_chat_id(kst)
    is_current = chat_id == normalize_chat_id(kst.chat_id)
    if is_current and kst.is_private:
        return await kst.eod("`Use this in for group/channel.`")
    if is_current:
        await kst.try_delete()
    try:
        await ga(
            fun.channels.DeleteChannelRequest(
                channel=chat_id,
            ),
        )
        if not is_current:
            await kst.eod(f"`Deleted channel {chat_id}.`")
    except BaseException:
        await kst.eod(f"`Cannot delete channel {chat_id}, try delete manually :(`")


plugins_help["chat"] = {
    "{i}read|{i}r": "Marks messages as read in current chat also clear mentions and reactions.",
    "{i}del|{i}d|d|D|del|Del": "Delete the replied message.",
    "{i}purge|{i}pg [reply]": "Purge messages from the replied message. This action cannot be undone!",
    "{i}purgeme|{i}pgm [number]/[reply]": "Purge my messages from given number or from replied message.",
    "{i}purgeall [reply]": "Delete all messages from replied user. This cannot be undone!",
    "{i}copy [reply]": "Copy the replied message.",
    "{i}nodraft": "Clear all drafts.",
    "{i}sd [seconds] [text]/[reply]": "Make self-destructible messages after particular time.",
    "{i}sdm [seconds] [text]/[reply]": "Same as sd command above but showing a note “self-destruct message in ? seconds”.",
    "{i}send|{i}dm [username/id] [text]/[reply]": "Send message to user or chat.",
    "{i}saved [reply]": "Save that replied message to Saved Messages or BOTLOGS for savedl.",
    "{i}fsaved [reply]": "Forward that replied message to Saved Messages or BOTLOGS for fsavedl.",
    "{i}react [reply]": "Give a random react to replied message.",
    "{i}ds|{i}ds1|{i}ds2|{i}ds3|{i}ds4 [seconds] [count] [reply]/[text]": "Spam current chat with delays in seconds (min 2 seconds) aka delayspam.",
    "{i}dscancel|{i}ds1cancel|{i}ds2cancel|{i}ds3cancel|{i}ds4cancel": "Stop the current delayspam.",
    "{i}report_spam [reply]/[in_private]/[username/mention/id]": "Report spam message from user.",
    "{i}invite [username/id]": "Add user to the current group/channel.",
    "{i}kickme [current/chat_id/username]/[reply]": "Leaves myself from group/channel.",
    "{i}archive [current/chat_id/username]/[reply]": "Move the groups/channels to archive folder.",
    "{i}unarchive [current/chat_id/username]/[reply]": "UnArchive the groups/channels from archive folder.",
    "{i}delchannel [current/chat_id/username]/[reply]": "Delete your group/channel.",
}
