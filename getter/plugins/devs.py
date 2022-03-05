# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import sys
from asyncio import sleep
from contextlib import suppress
from io import BytesIO
from os import (
    close,
    execl,
    name,
    system,
    getpid,
)
from secrets import choice
from time import time
import psutil as psu
from heroku3 import from_key
from telethon import functions
from . import (
    StartTime,
    Root,
    Var,
    DEVS,
    HELP,
    hl,
    eor,
    kasta_cmd,
    parse_pre,
    time_formatter,
)


async def heroku_logs(e):
    if not Var.HEROKU_API:
        await e.eor("Please set `HEROKU_API` in Config Vars.")
        return
    if not Var.HEROKU_APP_NAME:
        await e.eor("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        heroku_conn = from_key(Var.HEROKU_API)
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
    except Exception as err:
        await e.eor(f"**ERROR**\n`{err}`")
        return
    await e.eor("`Downloading Logs...`")
    logs = app.get_log()
    with open("app-heroku.log", "w") as f:
        f.write(logs)
    await e.client.send_file(
        e.chat_id,
        file="app-heroku.log",
        caption="Heroku Logs",
        force_document=True,
        allow_cache=False,
    )
    (Root / "app-heroku.log").unlink(missing_ok=True)
    await e.try_delete()


def restart_app():
    with suppress(psu.NoSuchProcess, psu.AccessDenied, psu.ZombieProcess):
        c_p = psu.Process(getpid())
        [close(h.fd) for h in c_p.open_files() + c_p.connections()]
    execl(sys.executable, sys.executable, "-m", "getter")
    return


@kasta_cmd(pattern="dea(c|k)$")
async def _(e):
    Kst = "[Delete Telegram Account](https://telegram.org/deactivate)"
    await e.eor(Kst)


@kasta_cmd(pattern="dc$")
async def _(e):
    result = await e.client(functions.help.GetNearestDcRequest())
    await e.eor(
        f"**Country:** `{result.country}`\n"
        f"**Nearest Datacenter:** `{result.nearest_dc}`\n"
        f"**This Datacenter:** `{result.this_dc}`"
    )


@kasta_cmd(disable_errors=True, pattern="ping|([pP]ing)$")
async def _(e):
    if hasattr(e, "text") and e.text.lower() not in [f"{hl}ping", "ping"]:
        return
    start = time()
    Kst = await eor(e, "Ping !")
    end = round((time() - start) * 1000)
    uptime = time_formatter((time() - StartTime) * 1000)
    await eor(
        Kst,
        f"🏓 Pong !!\n<b>Speed</b> - <code>{end}ms</code>\n<b>Uptime</b> - <code>{uptime}</code>",
        parse_mode="html",
    )


@kasta_cmd(disable_errors=True, pattern="logs?(?: |$)(heroku|hk|h)?(?: |$)(.*)")
@kasta_cmd(disable_errors=True, own=True, senders=DEVS, pattern="glogs?(?: |$)(heroku|hk|h)?(?: |$)(.*)")
async def _(e):
    is_devs = True if not (hasattr(e, "out") and e.out) else False
    mode = e.pattern_match.group(1)
    opt = e.pattern_match.group(2)
    if is_devs:
        user_id = None
        try:
            user_id = int(opt)
        except ValueError:
            pass
        if user_id and user_id != e.client.uid:
            return
        await sleep(choice((4, 6, 8)))
    with suppress(BaseException):
        Kst = await e.eor("`Getting...`", silent=True)
        if mode in ["heroku", "hk", "h"]:
            await heroku_logs(Kst)
        else:
            await Kst.reply("Terminal Logs", file="app.log", silent=True)
            await Kst.try_delete()


@kasta_cmd(pattern="restart$")
async def _(e):
    Kst = await e.eor("`Restarting...`")
    if name == "posix":
        _ = system("clear")
    await sleep(1)
    await Kst.eor("`Restarting the app, please wait for a minute!`")
    if not (Var.HEROKU_API and Var.HEROKU_APP_NAME):
        return restart_app()
    try:
        heroku_conn = from_key(Var.HEROKU_API)
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
        app.restart()
    except Exception as err:
        msg = await Kst.eor(f"**ERROR**\n`{err}`")
        await msg.reply("`Restarting as locally...`", silent=True)
        return restart_app()


@kasta_cmd(disable_errors=True, pattern="json$")
async def _(e):
    with suppress(BaseException):
        chat_id = e.chat_id or e.from_id
        Kst = (await e.get_reply_message()).stringify() if e.reply_to_msg_id else e.stringify()
        reply_to = e.reply_to_msg_id if e.reply_to_msg_id else e.id
        if len(Kst) > 4096:
            with BytesIO(str.encode(Kst)) as file:
                file.name = "json_output.txt"
                await e.client.send_file(
                    chat_id,
                    file=file,
                    force_document=True,
                    allow_cache=False,
                    reply_to=reply_to,
                )
            await e.try_delete()
        else:
            await e.eor(Kst, parse_mode=parse_pre)


HELP.update(
    {
        "devs": [
            "Devs",
            """❯ `{i}deak|{i}deac`
Give a link Deactivated Account.

❯ `{i}dc`
Finds the nearest datacenter from your server.

❯ `{i}ping|ping|Ping`
Check response time.

❯ `{i}logs`
Get the full terminal logs.

❯ `{i}logs <heroku|hk|h>`
Get the latest 100 lines of heroku logs.

❯ `{i}restart`
Restart the app.

❯ `{i}json <reply>`
Get the json encoding of the message.
""",
        ]
    }
)
