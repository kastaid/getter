# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import os
import sys
import time
import aiofiles
from telethon.tl import functions as fun
from . import (
    __version__,
    Root,
    kasta_cmd,
    plugins_help,
    choice,
    suppress,
    sgvar,
    parse_pre,
    format_exc,
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
    start_time = time.perf_counter()
    await kst.client(fun.PingRequest(ping_id=0))
    speedy = round(time.perf_counter() - start_time, 3)
    uptime = kst.client.uptime
    await kst.eor(
        f"🏓 Pong !!\n├  <b>Speedy</b> – <code>{speedy}ms</code>\n├  <b>Uptime</b> – <code>{uptime}</code>\n└  <b>Version</b> – <code>{__version__}</code>",
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
        with suppress(ValueError):
            user_id = int(opt)
        if user_id and user_id != kst.client.uid:
            return
        await asyncio.sleep(choice((4, 6, 8)))
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
            with suppress(BaseException):
                await yy.eor(
                    r"\\**#Getter**// Carbon Terminal Logs",
                    file=logs,
                    force_document=True,
                    allow_cache=False,
                )
            (Root / logs).unlink(missing_ok=True)
    elif mode == "open":
        for file in get_terminal_logs():
            logs = (Root / file).read_text()
            await yy.sod(logs, parts=True, parse_mode=parse_pre)
    else:
        with suppress(BaseException):
            for file in get_terminal_logs():
                await yy.eor(
                    r"\\**#Getter**// Terminal Logs",
                    file=file,
                    force_document=True,
                    allow_cache=False,
                )


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
        with suppress(ValueError):
            user_id = int(opt)
        if user_id and user_id != kst.client.uid:
            return
        await asyncio.sleep(choice((4, 6, 8)))
    yy = await kst.eor("`Restarting...`", silent=True)
    with suppress(BaseException):
        chat_id = yy.chat_id or yy.from_id
        sgvar("_restart", f"{chat_id}|{yy.id}")
    if not hk.is_heroku:
        await yy.eor(r"\\**#Getter**// `Restarting as locally...`")
        await restart_app()
        return
    try:
        await yy.eor(r"\\**#Getter**// `Restarting as heroku... Wait for a few minutes.`")
        app = hk.heroku().app(hk.name)
        app.restart()
    except Exception as err:
        reply = await yy.eor(format_exc(err), parse_mode="html")
        await reply.reply(r"\\**#Getter**// `Restarting as locally...`", silent=True)
        await restart_app()


@kasta_cmd(
    pattern="sleep(?: |$)(.*)",
)
async def _(kst):
    sec = await kst.client.get_text(kst)
    timer = int(sec) if sec.replace(".", "", 1).isdecimal() else 3
    timer = 3 if timer > 30 else timer
    yy = await kst.eor(f"`sleep in {timer} seconds...`")
    time.sleep(timer)
    await yy.eod(f"`wake-up from {timer} seconds`")


def get_terminal_logs():
    return sorted((Root / "logs").rglob("getter-*.log"))


async def heroku_logs(kst) -> None:
    if not hk.api:
        await kst.eod("Please set `HEROKU_API` in Config Vars.")
        return
    if not hk.name:
        await kst.eod("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        app = hk.heroku().app(hk.name)
        logs = app.get_log(lines=100)
    except Exception as err:
        return await kst.eor(format_exc(err), parse_mode="html")
    await kst.eor("`Downloading Logs...`")
    file = Root / "downloads/getter-heroku.log"
    async with aiofiles.open(file, mode="w") as f:
        await f.write(logs)
    await kst.eor(
        r"\\**#Getter**// Heroku Logs",
        file=file,
        force_document=True,
        allow_cache=False,
    )
    (file).unlink(missing_ok=True)


async def restart_app() -> None:
    with suppress(BaseException):
        import psutil

        proc = psutil.Process(os.getpid())
        for _ in proc.open_files() + proc.connections():
            os.close(_.fd)
    os.execl(sys.executable, sys.executable, "-m", "getter")


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
