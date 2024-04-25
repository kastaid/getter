# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import os
from asyncio import sleep
from random import choice
from sys import executable
from time import sleep as tsleep, monotonic
import aiofiles
from telethon.tl import functions as fun
from . import (
    __version__,
    Root,
    kasta_cmd,
    plugins_help,
    sgvar,
    parse_pre,
    formatx_send,
    Carbon,
    CARBON_PRESETS,
    hk,
)


@kasta_cmd(
    pattern="alive$",
)
async def _(kst):
    await kst.eod("**Hey, I am alive !!**")


@kasta_cmd(
    pattern="(uptime|up)$",
)
async def _(kst):
    await kst.eod(f"**Uptime:** {kst.client.uptime}")


@kasta_cmd(
    pattern="ping$|([p]ing)$",
    ignore_case=True,
    edited=True,
)
async def _(kst):
    start = monotonic()
    await kst.client(fun.PingRequest(ping_id=0))
    speedy = monotonic() - start
    uptime = kst.client.uptime
    await kst.eor(
        f"🏓 Pong !!\n├  <b>Speedy</b> – <code>{speedy:.3f}s</code>\n├  <b>Uptime</b> – <code>{uptime}</code>\n└  <b>Version</b> – <code>{__version__}</code>",
        parse_mode="html",
    )


@kasta_cmd(
    pattern="logs?(?: |$)(heroku|carbon|open)?",
)
@kasta_cmd(
    pattern="glogs?(?: |$)(heroku|carbon|open)?(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    mode = kst.pattern_match.group(1)
    if kst.is_dev:
        opt = kst.pattern_match.group(2)
        user_id = None
        try:
            user_id = int(opt)
        except ValueError:
            pass
        if user_id and user_id != kst.client.uid:
            return
        await sleep(choice((4, 6, 8)))
    yy = await kst.eor("`Getting...`", silent=True)
    if mode == "heroku":
        return await heroku_logs(yy)
    if mode == "carbon":
        theme = choice(tuple(CARBON_PRESETS))
        backgroundColor = CARBON_PRESETS[theme]
        for file in get_terminal_logs():
            code = (Root / file).read_text()
            logs = await Carbon(
                code.strip()[-2500:],
                file_name="carbon-getter-log",
                download=True,
                fontFamily="Hack",
                theme=theme,
                backgroundColor=backgroundColor,
                dropShadow=True,
            )
            if not logs:
                continue
            try:
                await yy.eor(
                    r"\\**#Getter**// Carbon Terminal Logs",
                    file=logs,
                    force_document=True,
                )
            except BaseException:
                pass
            (Root / logs).unlink(missing_ok=True)
    elif mode == "open":
        for file in get_terminal_logs():
            logs = (Root / file).read_text()
            await yy.sod(logs, parts=True, parse_mode=parse_pre)
    else:
        try:
            for file in get_terminal_logs():
                await yy.eor(
                    r"\\**#Getter**// Terminal Logs",
                    file=file,
                    force_document=True,
                )
        except BaseException:
            pass


@kasta_cmd(
    pattern="restart$",
)
@kasta_cmd(
    pattern="grestart(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        opt = kst.pattern_match.group(1)
        user_id = None
        try:
            user_id = int(opt)
        except ValueError:
            pass
        if user_id and user_id != kst.client.uid:
            return
        await sleep(choice((4, 6, 8)))
    yy = await kst.eor("`Restarting...`", silent=True)
    try:
        chat_id = yy.chat_id or yy.from_id
        await sgvar("_restart", f"{chat_id}|{yy.id}")
    except BaseException:
        pass
    if not hk.is_heroku:
        await yy.eor(r"\\**#Getter**// `Restarting as locally...`")
        return restart_app()
    try:
        await yy.eor(r"\\**#Getter**// `Restarting as heroku... Wait for a few minutes.`")
        app = hk.heroku().app(hk.name)
        app.restart()
    except Exception as err:
        reply = await yy.eor(formatx_send(err), parse_mode="html")
        await reply.reply(r"\\**#Getter**// `Restarting as locally...`", silent=True)
        restart_app()


@kasta_cmd(
    pattern="sleep(?: |$)(.*)",
)
async def _(kst):
    sec = await kst.client.get_text(kst)
    timer = int(sec) if sec.replace(".", "", 1).isdecimal() else 3
    timer = 3 if timer > 30 else timer
    yy = await kst.eor(f"`sleep in {timer} seconds...`")
    tsleep(timer)
    await yy.eod(f"`wake-up from {timer} seconds`")


def get_terminal_logs() -> list[Root]:
    return sorted((Root / "logs").rglob("getter-*.log"))


async def heroku_logs(kst) -> None:
    if not hk.api:
        return await kst.eod("Please set `HEROKU_API` in Config Vars.")
    if not hk.name:
        return await kst.eod("Please set `HEROKU_APP_NAME` in Config Vars.")
    try:
        app = hk.heroku().app(hk.name)
        logs = app.get_log(lines=100)
    except Exception as err:
        return await kst.eor(formatx_send(err), parse_mode="html")
    await kst.eor("`Downloading Logs...`")
    file = Root / "downloads/getter-heroku.log"
    async with aiofiles.open(file, mode="w") as f:
        await f.write(logs)
    await kst.eor(
        r"\\**#Getter**// Heroku Logs",
        file=file,
        force_document=True,
    )
    (file).unlink(missing_ok=True)


def restart_app() -> None:
    os.system("clear")
    try:
        import psutil

        proc = psutil.Process(os.getpid())
        for p in proc.open_files() + proc.connections():
            os.close(p.fd)
    except BaseException:
        pass
    reqs = Root / "requirements.txt"
    os.system(f"{executable} -m pip install --disable-pip-version-check --default-timeout=100 -U -r {reqs}")
    os.execl(executable, executable, "-m", "getter")


plugins_help["bot"] = {
    "{i}alive": "Just showing alive.",
    "{i}uptime|{i}up": "Check current uptime.",
    "{i}ping|ping|Ping": "Check how long it takes to ping.",
    "{i}logs": "Get the full terminal logs.",
    "{i}logs open": "Open logs as text message.",
    "{i}logs carbon": "Get the carbonized terminal logs.",
    "{i}logs heroku": "Get the latest 100 lines of heroku logs.",
    "{i}restart": "Restart the bot.",
    "{i}sleep [seconds]/[reply]": "Sleep the bot in few seconds (max 30).",
}
