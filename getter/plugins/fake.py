# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import datetime
import time
from . import (
    DEVS,
    kasta_cmd,
    plugins_help,
    choice,
    time_formatter,
    mentionuser,
    display_name,
    humanbool,
)

fgban_text = r"""
\\<b>#GBanned</b>// User {} in {} chats!
<b>Date:</b> <code>{}</code>
<b>Taken:</b> <code>{}</code>
<b>Reported:</b> <code>{}</code>
<b>Reason:</b> {}

<i>Added to GBanned_Watch.</i>
"""
fungban_text = r"""
\\<b>#UnGBanned</b>// User {} in {} chats!
<b>Taken:</b> <code>{}</code>

<i>Wait for 1 minutes before released.</i>
"""
_FGBAN_LOCK = asyncio.Lock()
_FUNGBAN_LOCK = asyncio.Lock()


@kasta_cmd(
    pattern="fgban(?: |$)((?s).*)",
)
@kasta_cmd(
    pattern="fgban(?: |$)((?s).*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gfgban(?: |$)((?s).*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    if not kst.is_dev and _FGBAN_LOCK.locked():
        await kst.eor("`Please wait until previous •gban• finished...`", time=5, silent=True)
        return
    async with _FGBAN_LOCK:
        ga = kst.client
        yy = await kst.eor("`GBanning...`", silent=True)
        user, reason = await ga.get_user(kst)
        if not user:
            return await yy.eor("`Reply to message or add username/id.`", time=5)
        if user.id == ga.uid:
            return await yy.eor("`Cannot gban to myself.`", time=3)
        if user.id in DEVS:
            return await yy.eor("`Forbidden to gban our awesome developers.`", time=3)
        start_time, date = time.time(), datetime.datetime.now().timestamp()
        done = 0
        if ga._dialogs:
            dialog = ga._dialogs
        else:
            dialog = await ga.get_dialogs()
            ga._dialogs.extend(dialog)
        for gg in dialog:
            if gg.is_group or gg.is_channel:
                await asyncio.sleep(0.2)
                done += 1
        taken = time_formatter((time.time() - start_time) * 1000)
        text = fgban_text.format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            done,
            datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d"),
            taken,
            humanbool(True),
            f"<pre>{reason}</pre>" if reason else "None given.",
        )
        await yy.eor(text, parse_mode="html")


@kasta_cmd(
    pattern="fungban(?: |$)(.*)",
)
@kasta_cmd(
    pattern="fungban(?: |$)(.*)",
    sudo=True,
)
@kasta_cmd(
    pattern="gfungban(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    if not kst.is_dev and _FUNGBAN_LOCK.locked():
        await kst.eor("`Please wait until previous •ungban• finished...`", time=5, silent=True)
        return
    async with _FUNGBAN_LOCK:
        ga = kst.client
        yy = await kst.eor("`UnGBanning...`", silent=True)
        user, _ = await ga.get_user(kst)
        if not user:
            return await yy.eor("`Reply to message or add username/id.`", time=5)
        if user.id == ga.uid:
            return await yy.eor("`Cannot ungban to myself.`", time=3)
        yy = await yy.reply("`Force UnGBanning...`", silent=True)
        start_time, done = time.time(), 0
        if ga._dialogs:
            dialog = ga._dialogs
        else:
            dialog = await ga.get_dialogs()
            ga._dialogs.extend(dialog)
        for gg in dialog:
            if gg.is_group or gg.is_channel:
                await asyncio.sleep(0.2)
                done += 1
        taken = time_formatter((time.time() - start_time) * 1000)
        text = fungban_text.format(
            mentionuser(user.id, display_name(user), width=15, html=True),
            done,
            taken,
        )
        await yy.eor(text, parse_mode="html")


plugins_help["fake"] = {
    "{i}fgban [reply]/[in_private]/[username/mention/id] [reason]": "Globally Fake Banned user in groups/channels.",
    "{i}fungban [reply]/[in_private]/[username/mention/id]": "Fake unban globally.",
}
