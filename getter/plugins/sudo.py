# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from datetime import datetime
from random import choice

from . import (
    SUDO_CMDS,
    TZ,
    del_col,
    dgvar,
    display_name,
    gvar,
    humanbool,
    jdata,
    kasta_cmd,
    plugins_help,
    set_col,
    sgvar,
)


@kasta_cmd(
    pattern="sudo(?: |$)(yes|on|true|1|no|off|false|0)?",
)
@kasta_cmd(
    pattern="gsudo(?: |$)(yes|on|true|1|no|off|false|0)?",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    toggle = kst.pattern_match.group(1)
    sudo = bool(await gvar("_sudo"))
    if not toggle:
        text = f"**Sudo Status:** `{humanbool(sudo, toggle=True)}`"
        return await yy.eod(text)
    if toggle in {"yes", "on", "true", "1"}:
        if sudo:
            return await yy.eor("`Sudo is already on.`", time=4)
        await sgvar("_sudo", "true")
        text = "`Successfully to switch on Sudo!`"
        text += "\n`Rebooting to apply...`"
        msg = await yy.eor(text)
        return await ga.reboot(msg)
    if not sudo:
        return await yy.eor("`Sudo is already off.`", time=4)
    await dgvar("_sudo")
    text = "`Successfully to switch off Sudo!`"
    text += "\n`Rebooting to apply...`"
    msg = await yy.eor(text)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="sudos$",
)
async def _(kst):
    cmds = "**Sudo Commands:**\n" + "\n".join(["- {}: {}".format(x, ", ".join(y)) for x, y in SUDO_CMDS.items()])
    await kst.sod(cmds, parts=True)


@kasta_cmd(
    pattern="addsudo(?: |$)(.*)",
)
@kasta_cmd(
    pattern="gaddsudo(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((4, 6, 8)))
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot add sudo to myself.`", time=3)
    if user.id in await jdata.sudo_users():
        return await yy.eor("`User is already sudo.`", time=4)
    full_name = display_name(user)
    userdata = {
        "full_name": full_name,
        "username": "@" + user.username if user.username else "none",
        "date": datetime.now(TZ).timestamp(),
    }
    sudos = await jdata.sudos()
    sudos[str(user.id)] = userdata
    await set_col("sudos", sudos)
    done = await yy.eor(f"<code>User {full_name} added to sudo list.</code>", parse_mode="html")
    msg = await done.reply("`Rebooting to apply...`", silent=True)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="delsudo(?: |$)(.*)",
)
@kasta_cmd(
    pattern="gdelsudo(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Processing...`", silent=True)
    user, _ = await ga.get_user(kst)
    if not user:
        return await yy.eor("`Reply to message or add username/id.`", time=5)
    if user.id == ga.uid:
        return await yy.eor("`Cannot delete sudo to myself.`", time=3)
    if user.id not in await jdata.sudo_users():
        return await yy.eor("`User is not sudo.`", time=4)
    full_name = display_name(user)
    sudos = await jdata.sudos()
    del sudos[str(user.id)]
    await set_col("sudos", sudos)
    done = await yy.eor(f"<code>User {full_name} deleted in sudo list.</code>", parse_mode="html")
    msg = await done.reply("`Rebooting to apply...`", silent=True)
    await ga.reboot(msg)


@kasta_cmd(
    pattern="listsudo$",
)
async def _(kst):
    sudo_users = await jdata.sudo_users()
    total = len(sudo_users)
    if total > 0:
        text = f"<b><u>{total} Sudo Users</u></b>\n"
        sudos = await jdata.sudos()
        for x in sudo_users:
            user_id = str(x)
            text += "User: {}\n".format(sudos[user_id]["full_name"])
            text += f"User ID: {x}\n"
            text += "Username: {}\n".format(sudos[user_id]["username"])
            text += "Date: {}\n\n".format(datetime.fromtimestamp(sudos[user_id]["date"]).strftime("%Y-%m-%d"))
        return await kst.eor(text, parts=True, parse_mode="html")
    text = "`You got no sudo users!`"
    await kst.eor(text, time=5)


@kasta_cmd(
    pattern="delallsudos$",
)
async def _(kst):
    if not await jdata.sudo_users():
        return await kst.eor("`You got no sudo users!`", time=3)
    await del_col("sudos")
    done = await kst.eor("`Successfully to delete all sudo users!`")
    msg = await done.reply("`Rebooting to apply...`", silent=True)
    await kst.client.reboot(msg)


plugins_help["sudo"] = {
    "{i}sudo [yes/no/on/off]": "Switch the sudo commands on or off. Default: off",
    "{i}sudos": "List all sudo commands.",
    "{i}addsudo [reply]/[in_private]/[username/mention/id]": "Add user to sudo list.",
    "{i}delsudo [reply]/[in_private]/[username/mention/id]": "Delete user from sudo list.",
    "{i}listsudo": "List all sudo users.",
    "{i}delallsudos": """Delete all sudo users.

**Note:**
- Handler for sudo commands is [ , ] comma. E.g: `,test`
- The sudo, addsudo, delsudo, and delsudos commands are automatically reboot after changes, this to apply changes!
""",
}
