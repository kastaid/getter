# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import datetime
import html
import time
from cachetools import TTLCache
from telethon.tl import functions as fun, types as typ
from . import (
    DEVS,
    getter_app,
    kasta_cmd,
    sendlog,
    plugins_help,
    DEFAULT_GUCAST_BLACKLIST,
    get_blacklisted,
    events,
    choice,
    suppress,
    dgvar,
    sgvar,
    gvar,
    add_col,
    jdata,
    display_name,
    mentionuser,
    humanbool,
    replace_all,
    is_allow,
    allow_user,
    deny_user,
    all_allow,
    deny_all,
)

pmcredit = "\n- Protected by getter"
pmtotal_default = 3
pmbye_default = "~ You are automatically {mode}!"
pmmsg_default = """Hello {fullname} this is an automated message,
Please wait until you got allowed to PM,
And please Do Not Spam!

You have {warn}/{total} warns until you got {mode}!"""
_TORM = {
    "`": "",
    "*": "",
    "_": "",
    "-": "",
    "~": "",
}
_PMBYE_CACHE = TTLCache(maxsize=1, ttl=60, timer=time.perf_counter)  # 1 mins
_PMMSG_CACHE = TTLCache(maxsize=1, ttl=60, timer=time.perf_counter)  # 1 mins
_PMTOTAL_CACHE = TTLCache(maxsize=1, ttl=60, timer=time.perf_counter)  # 1 mins


async def PMLogs(kst):
    user = await kst.get_sender()
    if (
        getattr(user, "bot", False)
        or getattr(user, "is_self", False)
        or getattr(user, "support", False)
        or getattr(user, "verified", False)
    ):
        return
    pmlog = gvar("_pmlog", use_cache=True)
    if pmlog == "media":
        if kst.message.media:
            return await sendlog(kst.message, forward=True)
        return
    await sendlog(kst.message, forward=True)


async def PMPermit(kst):
    user = await kst.get_sender()
    if (
        getattr(user, "bot", False)
        or getattr(user, "is_self", False)
        or getattr(user, "support", False)
        or getattr(user, "verified", False)
        or getattr(user, "contact", False)
    ):
        return
    GUCAST_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/gucastblacklist.py",
        attempts=1,
        fallbacks=DEFAULT_GUCAST_BLACKLIST,
    )
    if user.id in {*DEVS, *GUCAST_BLACKLIST}:
        return
    if is_allow(user.id, use_cache=True):
        return
    ga = kst.client
    towarn = str(user.id)
    PMWARN, NESLAST = jdata.pmwarns(), jdata.pmlasts()
    antipm = gvar("_antipm", use_cache=True)
    if antipm:
        if towarn in PMWARN:
            del PMWARN[towarn]
            add_col("pmwarns", PMWARN, NESLAST)
        mention = mentionuser(user.id, display_name(user), width=70)
        antipm_text = r"\\**#Anti_PM**//"
        antipm_text += f"\nUser {mention} [`{user.id}`] has messaged you and got "
        await ga.report_spam(user.id)
        await ga.block(user.id)
        if antipm == "del":
            antipm_text += "blocked and deleted!"
            await sendlog(antipm_text)
            await sendlog(kst.message, forward=True)
            await ga.delete_chat(user.id, revoke=True)
        else:
            antipm_text += "blocked!"
            await sendlog(antipm_text)
        return
    if towarn not in PMWARN:
        PMWARN[towarn] = 0
    PMWARN[towarn] += 1
    warn = PMWARN[towarn]
    if "_pmtotal" in _PMTOTAL_CACHE:
        ratelimit = _PMTOTAL_CACHE.get("_pmtotal")
    else:
        ratelimit = int(gvar("_pmtotal") or pmtotal_default)
        _PMTOTAL_CACHE["_pmtotal"] = ratelimit
    name = " ".join(replace_all(user.first_name, _TORM).split())
    last = " ".join(replace_all(user.last_name, _TORM).split()) if user.last_name else ""
    fullname = f"{name} {last}".rstrip()
    mention = mentionuser(user.id, fullname, width=70)
    username = f"@{user.username}" if user.username else mention
    me, my_id = ga.me, ga.uid
    my_name = " ".join(replace_all(me.first_name, _TORM).split())
    my_last = " ".join(replace_all(me.last_name, _TORM).split()) if me.last_name else ""
    my_fullname = f"{my_name} {my_last}".rstrip()
    my_mention = mentionuser(my_id, my_fullname, width=70)
    my_username = f"@{me.username}" if me.username else my_mention
    is_block = bool(gvar("_pmblock", use_cache=True))
    mode = "blocked" if is_block else "archived"
    if PMWARN[towarn] > ratelimit:
        warnend_text = f"\nUser {mention} [`{user.id}`] has been "
        with suppress(BaseException):
            await ga.delete_messages(user.id, [NESLAST[towarn]])
        if "_pmbye" in _PMBYE_CACHE:
            pmbye = _PMBYE_CACHE.get("_pmbye")
        else:
            pmbye = gvar("_pmbye") or pmbye_default
            _PMBYE_CACHE["_pmbye"] = pmbye
        text = pmbye.format(
            id=user.id,
            name=name,
            fullname=fullname,
            mention=mention,
            username=username,
            my_id=my_id,
            my_name=my_name,
            my_fullname=my_fullname,
            my_mention=my_mention,
            my_username=my_username,
            warn=warn,
            total=ratelimit,
            mode=mode,
        )
        text += pmcredit
        with suppress(BaseException):
            await kst.respond(text)
        if is_block:
            await ga.read(user.id, clear_mentions=True, clear_reactions=True)
            with suppress(BaseException):
                await ga(
                    fun.account.ReportPeerRequest(
                        user.id,
                        reason=typ.InputReportReasonSpam(),
                        message="Sends spam messages to my account. I ask Telegram to ban such user.",
                    )
                )
            await ga.block(user.id)
            warnend_text += "blocked due to spamming in PM !!"
            await sendlog(r"\\**#Blocked**//" + warnend_text)
        else:
            await ga.archive(user.id)
            warnend_text += "archived due to spamming in PM !!"
            await sendlog(r"\\**#Archived**//" + warnend_text)
        del PMWARN[towarn]
        add_col("pmwarns", PMWARN, NESLAST)
        return
    if "_pmmsg" in _PMMSG_CACHE:
        pmmsg = _PMMSG_CACHE.get("_pmmsg")
    else:
        pmmsg = gvar("_pmmsg") or pmmsg_default
        _PMMSG_CACHE["_pmmsg"] = pmmsg
    text = pmmsg.format(
        id=user.id,
        name=name,
        fullname=fullname,
        mention=mention,
        username=username,
        my_id=my_id,
        my_name=my_name,
        my_fullname=my_fullname,
        my_mention=my_mention,
        my_username=my_username,
        warn=warn,
        total=ratelimit,
        mode=mode,
    )
    text += pmcredit
    with suppress(BaseException):
        await ga.delete_messages(user.id, [NESLAST[towarn]])
    await asyncio.sleep(1)
    last = await kst.reply(text)
    NESLAST[towarn] = last.id
    add_col("pmwarns", PMWARN, NESLAST)
    # await ga.read(user.id, clear_mentions=True, clear_reactions=True)
    newmsg_text = r"\\**#New_Message**//"
    newmsg_text += f"\nUser {mention} [`{user.id}`] has messaged you with **{warn}/{ratelimit}** warns!"
    await sendlog(newmsg_text)
    if not gvar("_pmlog", use_cache=True):
        await asyncio.sleep(1)
        await sendlog(kst.message, forward=True)


@kasta_cmd(
    pattern="pmguard(?: |$)(yes|on|true|1|no|off|false|0)?",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    toggle = kst.pattern_match.group(1)
    pmguard = bool(gvar("_pmguard"))
    if not toggle:
        text = f"**PM-Guard Status:** `{humanbool(pmguard, toggle=True)}`"
        return await yy.eod(text)
    if toggle in ("yes", "on", "true", "1"):
        if pmguard:
            await yy.eor("`PM-Guard is already on.`", time=4)
            return
        sgvar("_pmguard", "true")
        text = "`Successfully to switch on PM-Guard!`"
        text += "\n`Rebooting to apply...`"
        msg = await yy.eor(text)
        return await ga.reboot(msg)
    if not pmguard:
        await yy.eor("`PM-Guard is already off.`", time=4)
        return
    dgvar("_pmguard")
    text = "`Successfully to switch off PM-Guard!`"
    text += "\n`Rebooting to apply...`"
    msg = await yy.eor(text)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="pmlogs?(?: |$)(yes|on|true|1|no|off|false|0)?(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    group = kst.pattern_match.group
    toggle, opts = group(1), group(2).lower()
    pmlog = gvar("_pmlog")
    if not toggle:
        text = f"**PM-Logs Status:** `{humanbool(pmlog, toggle=True)}`"
        if pmlog and pmlog == "media":
            text += "\n__Only media!__"
        return await yy.eod(text)
    if toggle in ("yes", "on", "true", "1"):
        if pmlog:
            await yy.eor("`PM-Logs is already on.`", time=4)
            return
        if opts and any(_ in opts for _ in ("-m", "media")):
            sgvar("_pmlog", "media")
            text = "`Successfully to switch on-media PM-Logs!`"
        else:
            sgvar("_pmlog", "true")
            text = "`Successfully to switch on PM-Logs!`"
        text += "\n`Rebooting to apply...`"
        msg = await yy.eor(text)
        return await ga.reboot(msg)
    if not pmlog:
        await yy.eor("`PM-Logs is already off.`", time=4)
        return
    dgvar("_pmlog")
    text = "`Successfully to switch off PM-Logs!`"
    text += "\n`Rebooting to apply...`"
    msg = await yy.eor(text)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="(a|allow|acc)(?: |$)(.*)",
)
@kasta_cmd(
    pattern="g(a|allow|acc)(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, reason = await ga.get_user(kst, group=2)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot allow to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Our devs auto allowed!`", time=3)
    if is_allow(user.id):
        return await yy.eor("`User is already Allowed.`", time=4)
    date = datetime.datetime.now().timestamp()
    allow_user(user.id, date, reason)
    text = "<b><u>User {} allowed to PM!</u></b>\n".format(display_name(user))
    text += "<b>Date:</b> <code>{}</code>\n".format(datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d"))
    text += "<b>Reason:</b> {}".format(f"<pre>{reason}</pre>" if reason else "None given.")
    done = await yy.eor(text, parse_mode="html")
    towarn, PMWARN = str(user.id), jdata.pmwarns()
    if towarn in PMWARN:
        del PMWARN[towarn]
        add_col("pmwarns", PMWARN, jdata.pmlasts())
    msg = await done.reply("`Rebooting to apply...`", silent=True)
    await kst.client.reboot(msg)


@kasta_cmd(
    pattern="(de|deny)(?: |$)(.*)",
)
@kasta_cmd(
    pattern="g(de|deny)(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot deny to myself.`", time=3)
    deny_user(user.id)
    done = await yy.eor(f"<code>User {display_name(user)} disallowed to PM!</code>", parse_mode="html")
    msg = await done.reply("`Rebooting to apply...`", silent=True)
    await kst.client.reboot(msg)


@kasta_cmd(
    pattern="listpm$",
)
async def _(kst):
    allowed_users = all_allow()
    total = len(allowed_users)
    if total > 0:
        text = f"<b><u>{total} Allowed Users PM</u></b>\n"
        for x in allowed_users:
            text += f"User ID: {x.user_id}\n"
            text += "Date: {}\n".format(datetime.datetime.fromtimestamp(x.date).strftime("%Y-%m-%d"))
            text += "Reason: {}\n".format(x.reason or "None given.")
        return await kst.eor(text, parts=True, parse_mode="html")
    text = "`You got no allowed users!`"
    await kst.eor(text, time=5)


@kasta_cmd(
    pattern="denyall$",
)
async def _(kst):
    if not all_allow():
        return await kst.eor("`You got no allowed users!`", time=3)
    deny_all()
    done = await kst.eor("`Successfully to delete all allowed users!`")
    msg = await done.reply("`Rebooting to apply...`", silent=True)
    await kst.client.reboot(msg)


@kasta_cmd(
    pattern="pmblock(?: |$)(yes|on|true|1|no|off|false|0)?",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    toggle = kst.pattern_match.group(1)
    pmblock = bool(gvar("_pmblock"))
    if not toggle:
        text = f"**PM-Block Status:** `{humanbool(pmblock, toggle=True)}`"
        return await yy.eod(text)
    if toggle in ("yes", "on", "true", "1"):
        if pmblock:
            await yy.eor("`PM-Block is already on.`", time=4)
            return
        sgvar("_pmblock", "true")
        text = "`Successfully to switch on PM-Block!`"
        text += "\n`Rebooting to apply...`"
        msg = await yy.eor(text)
        return await ga.reboot(msg)
    if not pmblock:
        await yy.eor("`PM-Block is already off.`", time=4)
        return
    dgvar("_pmblock")
    text = "`Successfully to switch off PM-Block!`"
    text += "\n`Rebooting to apply...`"
    msg = await yy.eor(text)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="antipm(?: |$)(yes|on|true|1|no|off|false|0)?(?: |$)(.*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    group = kst.pattern_match.group
    toggle, opts = group(1), group(2).lower()
    antipm = gvar("_antipm")
    if not toggle:
        text = f"**Anti-PM Status:** `{humanbool(antipm, toggle=True)}`"
        if antipm and antipm == "del":
            text += "\n__With delete chat!__"
        return await yy.eod(text)
    if toggle in ("yes", "on", "true", "1"):
        if antipm:
            await yy.eor("`Anti-PM is already on.`", time=4)
            return
        if opts and any(_ in opts for _ in ("-d", "delete")):
            sgvar("_antipm", "del")
            text = "`Successfully to switch on-delete Anti-PM!`"
        else:
            sgvar("_antipm", "true")
            text = "`Successfully to switch on Anti-PM!`"
        text += "\n`Rebooting to apply...`"
        msg = await yy.eor(text)
        return await ga.reboot(msg)
    if not antipm:
        await yy.eor("`Anti-PM is already off.`", time=4)
        return
    dgvar("_antipm")
    text = "`Successfully to switch off Anti-PM!`"
    text += "\n`Rebooting to apply...`"
    msg = await yy.eor(text)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="setpm(bye|msg|total)(?: |$)((?s).*)",
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`")
    custom = await ga.get_text(
        kst,
        group=2,
        plain=False,
        strip=False,
    )
    cmd = kst.pattern_match.group(1)
    if cmd == "bye":
        mode = "pmbye"
        pmbye = gvar("_pmbye")
        if not custom:
            text = "<b>PM-Bye:</b>\n"
            text += "<pre>{}</pre>".format(html.escape(pmbye or pmbye_default))
            await yy.eor(text, parse_mode="html")
            return
        if pmbye == custom:
            return await yy.eor(f"`{mode} is already set.`", time=4)
        sgvar("_pmbye", custom)
    elif cmd == "msg":
        mode = "pmmsg"
        pmmsg = gvar("_pmmsg")
        if not custom:
            text = "<b>PM-Message:</b>\n"
            text += "<pre>{}</pre>".format(html.escape(pmmsg or pmmsg_default))
            await yy.eor(text, parse_mode="html")
            return
        if pmmsg == custom:
            return await yy.eor(f"`{mode} is already set.`", time=4)
        sgvar("_pmmsg", custom)
    elif cmd == "total":
        mode = "pmtotal"
        pmtotal = gvar("_pmtotal")
        custom = custom.strip()
        if not custom:
            text = "**PM-Total:** `{}`".format(pmtotal or pmtotal_default)
            await yy.eod(text)
            return
        if not custom.isdecimal():
            return await yy.eor("`Provide a valid number!`", time=5)
        if int(custom) <= 1:
            return await yy.eor(f"`{mode} must be greater than 1.`", time=4)
        if pmtotal and int(pmtotal) == int(custom):
            return await yy.eor(f"`{mode} is already set.`", time=4)
        sgvar("_pmtotal", custom)
    text = f"`Successfully to set {mode}!`"
    await yy.eor(text)


@kasta_cmd(
    pattern="resetpm(bye|msg|total)$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    cmd = kst.pattern_match.group(1)
    if cmd == "bye":
        mode = "pmbye"
        if not gvar("_pmbye"):
            return await yy.eor(f"`{mode} is already default.`", time=4)
        dgvar("_pmbye")
    elif cmd == "msg":
        mode = "pmmsg"
        if not gvar("_pmmsg"):
            return await yy.eor(f"`{mode} is already default.`", time=4)
        dgvar("_pmmsg")
    elif cmd == "total":
        mode = "pmtotal"
        if not gvar("_pmtotal"):
            return await yy.eor(f"`{mode} is already default.`", time=4)
        dgvar("_pmtotal")
    text = f"`Successfully to reset {mode}!`"
    await yy.eor(text)


@kasta_cmd(
    pattern="block(?: |$)(.*)",
)
@kasta_cmd(
    pattern="block(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gblock(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    chat_id = kst.chat_id
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot block to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to block our awesome developers.`", time=3)
    is_reported = False
    await ga.unblock(user.id)
    with suppress(BaseException):
        if kst.is_private:
            is_reported = await ga(
                fun.account.ReportPeerRequest(
                    user.id,
                    reason=typ.InputReportReasonSpam(),
                    message="Sends spam messages to my account. I ask Telegram to ban such user.",
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
    is_block = await ga.block(user.id)
    if is_block:
        text = "`User blocked and {} reported!`".format("was" if is_reported else "not")
    else:
        text = "`Cannot Block!`"
    towarn, PMWARN = str(user.id), jdata.pmwarns()
    if towarn in PMWARN:
        del PMWARN[towarn]
        add_col("pmwarns", PMWARN, jdata.pmlasts())
    if kst.is_dev or kst.is_sudo:
        return await yy.eor(text)
    await yy.eod(text)


@kasta_cmd(
    pattern="unblock(?: |$)(.*)",
)
@kasta_cmd(
    pattern="unblock(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gunblock(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot unblock to myself.`", time=3)
    is_unblock = await ga.unblock(user.id)
    if is_unblock:
        text = "`User UnBlocked!`"
    else:
        text = "`Cannot UnBlock!`"
    if kst.is_dev or kst.is_sudo:
        return await yy.eor(text)
    await yy.eod(text)


@kasta_cmd(
    pattern="move(?: |$)(.*)",
)
@kasta_cmd(
    pattern="move(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gmove(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot archive to myself.`", time=3)
    if user.id in DEVS:
        return await yy.eor("`Forbidden to archive our awesome developers.`", time=3)
    is_archive = await ga.archive(user.id)
    if not (is_archive is None):
        text = "`Archived!`"
    else:
        text = "`Cannot Archive!`"
    towarn, PMWARN = str(user.id), jdata.pmwarns()
    if towarn in PMWARN:
        del PMWARN[towarn]
        add_col("pmwarns", PMWARN, jdata.pmlasts())
    if kst.is_dev or kst.is_sudo:
        return await yy.eor(text)
    await yy.eod(text)


@kasta_cmd(
    pattern="unmove(?: |$)(.*)",
)
@kasta_cmd(
    pattern="unmove(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gunmove(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot unarchive to myself.`", time=3)
    is_unarchive = await ga.unarchive(user.id)
    if not (is_unarchive is None):
        text = "`UnArchived!`"
    else:
        text = "`Cannot UnArchive!`"
    if kst.is_dev or kst.is_sudo:
        return await yy.eor(text)
    await yy.eod(text)


@kasta_cmd(
    pattern="delete$",
    no_chats=True,
    chats=DEVS,
    private_only=True,
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    if chat_id == ga.uid:
        return await kst.eor("`Cannot delete myself, protected!`", time=5)
    towarn, PMWARN = str(chat_id), jdata.pmwarns()
    if towarn in PMWARN:
        del PMWARN[towarn]
        add_col("pmwarns", PMWARN, jdata.pmlasts())
    await ga.delete_chat(chat_id, revoke=True)


if gvar("_pmlog", use_cache=True):
    getter_app.add_handler(
        PMLogs,
        event=events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private,
        ),
    )
if gvar("_pmguard", use_cache=True):
    getter_app.add_handler(
        PMPermit,
        event=events.NewMessage(
            incoming=True,
            func=lambda e: e.is_private,
        ),
    )

plugins_help["pmpermit"] = {
    "{i}pmguard [yes/no/on/off]": "Switch the pmpermit plugin on or off. Default: off",
    "{i}pmlog [yes/no/on/off] [-m/media]": "When switch on all messages from user will forward to BOTLOGS! Add '-m' to forward media only! Default: off",
    "{i}a|{i}allow|{i}acc [reply]/[in_private]/[username/mention/id]": "Allow user to PM.",
    "{i}de|{i}deny [reply]/[in_private]/[username/mention/id]": "Delete user from allowed list.",
    "{i}listpm": "List all allowed users to PM.",
    "{i}denyall": "Delete all allowed users.",
    "{i}pmblock [yes/no/on/off]": "When switch on user got reported as spam and blocked, when off user got archived. Default: off",
    "{i}antipm [yes/no/on/off] [-d/delete]": "When switch on user got reported as spam and blocked! Except users who are not in contact book and allowed users. Add '-d' to delete the chat too (delete chat cannot be undone)! Default: off",
    "{i}setpmbye [text]/[reply]": "Sets the goodbye message or get current text. Supports markdown with format in below.",
    "{i}setpmmsg [text]/[reply]": "Sets the automated message or get current text. Supports markdown with format in below.",
    "{i}setpmtotal [number]": f"Sets the total message will repeat before archived or blocked. Number must be greater than 1. Default: {pmtotal_default}",
    "{i}resetpmbye": "Reset the pmbye to default.",
    "{i}resetpmmg": "Reset the pmmsg to default.",
    "{i}resetpmtotal": "Reset the pmtotal to default.",
    "{i}block [reply]/[in_private]/[username/mention/id]": "Block user and report them as spam.",
    "{i}unblock [reply]/[in_private]/[username/mention/id]": "Unblock user.",
    "{i}move [reply]/[in_private]/[username/mention/id]": "Move user to archive folder.",
    "{i}unmove [reply]/[in_private]/[username/mention/id]": "Unarchive user.",
    "{i}delete": """Delete and revoke current PM also for bots but exclude myself. This action cannot be undone!

**Note:**
- The pmguard, allow, deny, denyall, pmblock, and antipm commands are automatically reboot after changes, this to apply changes!
- The setpmbye, setpmmsg, and setpmtotal commands are not rebooted, but it's cached in 1 minutes.

**Format for pmbye and pmmsg:**
`{id}`: The user ID.
`{name}`: The user first name.
`{fullname}`: The user full name.
`{mention}`: Mentions the user with full name.
`{username}`: The user username. If they don't have one, mentions the user instead.
`{my_id}`: My ID.
`{my_name}`: My first name.
`{my_fullname}`: My full name.
`{my_mention}`: Mentions myself with full name.
`{my_username}`: My username. If don't have one, mentions myself instead.
`{warn}`: The user's warns.
`{total}`: Total a warns.
`{mode}`: The pmblock mode (archived or blocked).
""",
}
