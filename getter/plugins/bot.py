# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import os
import random
import subprocess
import sys
from time import monotonic, sleep as tsleep
from typing import TYPE_CHECKING

from telethon.tl import functions as fun

from . import (
    CARBON_PRESETS,
    DOWNLOAD_DIR,
    LOG_DIR,
    Carbon,
    Root,
    StartTime,
    format_latency,
    format_time,
    formatx_send,
    hk,
    kasta_cmd,
    parse_pre,
    plugins_help,
    sgvar,
)

if TYPE_CHECKING:
    from pathlib import Path


@kasta_cmd(
    pattern="alive$",
)
async def _(kst):
    await kst.eod("**Hey, I am alive !!**")


@kasta_cmd(
    pattern="(uptime|up)$",
)
async def _(kst):
    await kst.eod(f"**Uptime**: {kst.client.uptime}")


@kasta_cmd(
    pattern="ping$|([p]ing)$",
    ignore_case=True,
    edited=True,
)
async def _(kst):
    start = monotonic()
    task = asyncio.ensure_future(kst.client(fun.PingRequest(ping_id=0)))
    _done, pending = await asyncio.wait({task}, timeout=8.0)
    if task in pending:
        pass
    else:
        try:
            task.result()
        except Exception:
            pass
    text = f"Speed – {format_latency(monotonic() - start)}\n"
    text += "Uptime – {}".format(
        format_time(
            monotonic() - StartTime,
            short=True,
        )
    )
    await kst.eor(text)


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
        await asyncio.sleep(random.choice((4, 6, 8)))
    yy = await kst.eor("`Getting...`", silent=True)
    if mode == "heroku":
        return await heroku_logs(yy)
    if mode == "carbon":
        theme = random.choice(tuple(CARBON_PRESETS))
        backgroundColor = CARBON_PRESETS[theme]
        for file in get_terminal_logs():
            code = await asyncio.to_thread(file.read_text)
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
            await asyncio.to_thread(logs.unlink, missing_ok=True)
    elif mode == "open":
        for file in get_terminal_logs():
            logs = await asyncio.to_thread(file.read_text)
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
        await asyncio.sleep(random.choice((4, 6, 8)))
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
    tsleep(timer)  # noqa: ASYNC251
    await yy.eod(f"`wake-up from {timer} seconds`")


def get_terminal_logs() -> list[Path]:
    return sorted(LOG_DIR.glob("*.log"))


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
    file = DOWNLOAD_DIR / "getter-heroku.log"
    await asyncio.to_thread(file.write_text, logs, encoding="utf-8")
    await kst.eor(
        r"\\**#Getter**// Heroku Logs",
        file=file,
        force_document=True,
    )
    await asyncio.to_thread(file.unlink, missing_ok=True)


def restart_app() -> None:
    try:
        import psutil

        proc = psutil.Process(os.getpid())
        for p in proc.open_files() + proc.connections():
            os.close(p.fd)
    except BaseException:
        pass
    reqs = str(Root / "requirements.txt")
    try:
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "-r",
                reqs,
            ],
            check=True,
        )
    except FileNotFoundError:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--prefer-binary",
                "--disable-pip-version-check",
                "--default-timeout=100",
                "-r",
                reqs,
            ],
            check=True,
        )
    os.execl(sys.executable, sys.executable, "-m", "getter")


plugins_help["bot"] = {
    "{pfx}alive": "Just showing alive.",
    "{pfx}uptime|{pfx}up": "Check current uptime.",
    "{pfx}ping|ping|Ping": "Check how long it takes to ping.",
    "{pfx}logs": "Get the full terminal logs.",
    "{pfx}logs open": "Open logs as text message.",
    "{pfx}logs carbon": "Get the carbonized terminal logs.",
    "{pfx}logs heroku": "Get the latest 100 lines of heroku logs.",
    "{pfx}restart": "Restart the bot.",
    "{pfx}sleep [seconds]/[reply]": "Sleep the bot in few seconds (max 30).",
}
