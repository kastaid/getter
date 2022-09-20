# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import html
import json
import os
import sys
import time
from io import BytesIO
from pathlib import Path
import aiofiles
from telethon.tl import functions as fun
from . import (
    __version__,
    Root,
    DEV_CMDS,
    DEVS,
    kasta_cmd,
    plugins_help,
    choice,
    suppress,
    sgvar,
    strip_format,
    parse_pre,
    humanbytes,
    to_dict,
    Runner,
    Carbon,
    LSFILES_MAP,
    MAX_MESSAGE_LEN,
    CARBON_PRESETS,
    DEFAULT_SHELL_BLACKLIST,
    get_blacklisted,
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
    else:
        await yy.try_delete()
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
                await kst.respond(
                    r"\\**#Getter**// Carbon Terminal Logs",
                    file=logs,
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id,
                    silent=True,
                )
            (Root / logs).unlink(missing_ok=True)
    elif mode == "open":
        for file in get_terminal_logs():
            logs = (Root / file).read_text()
            await yy.sod(logs, parse_mode=parse_pre)
    else:
        with suppress(BaseException):
            for file in get_terminal_logs():
                await kst.respond(
                    r"\\**#Getter**// Terminal Logs",
                    file=file,
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id,
                    silent=True,
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
        sgvar("_restart", f"{kst.chat_id}|{yy.id}")
    if not hk.is_heroku:
        await yy.eor(r"\\**#Getter**// `Restarting as locally...`")
        await restart_app()
        return
    try:
        await yy.eor(r"\\**#Getter**// `Restarting as heroku... Wait for a few minutes.`")
        app = hk.heroku().app(hk.name)
        app.restart()
    except Exception as err:
        reply = await yy.eor(f"**ERROR:**\n`{err}`")
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


@kasta_cmd(
    pattern="(raw|json)$",
)
async def _(kst):
    mode = kst.pattern_match.group(1)
    msg = await kst.get_reply_message() if kst.is_reply else kst
    if mode == "json":
        text = json.dumps(
            to_dict(msg),
            indent=2,
            default=str,
            sort_keys=False,
        )
    else:
        text = msg.stringify()
    await kst.eor(f"<pre>{html.escape(text)}</pre>", parse_mode="html")


@kasta_cmd(
    pattern="sysinfo$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    file = "downloads/neofetch.txt"
    _, _, ret, _ = await Runner(f"neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g'>>{file}")
    if ret != 0:
        return await yy.try_delete()
    info = (Root / file).read_text()
    theme = choice(tuple(CARBON_PRESETS))
    backgroundColor = CARBON_PRESETS[theme]
    neofetch = await Carbon(
        info.replace("\n\n", "").strip(),
        file_name="neofetch",
        fontFamily="Hack",
        theme=theme,
        backgroundColor=backgroundColor,
        dropShadow=True,
    )
    if not neofetch:
        return await yy.try_delete()
    with suppress(BaseException):
        await kst.respond(
            file=neofetch,
            force_document=False,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await yy.try_delete()
    (Root / file).unlink(missing_ok=True)


@kasta_cmd(
    pattern="ls(?: |$)(.*)",
)
async def _(kst):
    cat = await kst.client.get_text(kst)
    if not cat:
        cat = "*"
    elif cat.endswith("/"):
        cat += "*"
    elif "*" not in cat:
        cat += "/*"
    yy = await kst.eor("`Loading...`")
    try:
        paths = sorted(Path(".").glob(cat))
    except BaseException:
        paths = None
    if not paths:
        return await yy.eor("`No such directory or empty or incorrect.`", time=5)
    _symlinks, _folders, _dockers, _allfiles = [], [], [], []
    for p in paths:
        if p.is_symlink():
            _symlinks.append(("🔗", p))
        elif p.is_dir():
            _folders.append(("📂", p))
        elif "docker" in str(p).lower():
            _dockers.append(("🐋", p))
        else:
            for x in LSFILES_MAP:
                if p.suffix in x:
                    _allfiles.append((LSFILES_MAP[x], p))
                    break
            else:
                if p.is_file():
                    _allfiles.append(("🏷️", p))
                else:
                    _allfiles.append(("📒", p))
    lists = [
        *sorted(_folders),
        *sorted(_symlinks),
        *sorted(_allfiles),
        *sorted(_dockers),
    ]
    directory = ""
    sfile, sfolder, cfile, cfolder = 0, 0, 0, 0
    for emoji, path in lists:
        with suppress(BaseException):
            if path.is_dir():
                size = 0
                for p in path.rglob("*"):
                    size += p.stat().st_size
                directory += emoji + f" <code>{path.name}</code>  <code>{humanbytes(size)}</code>\n"
                sfolder += size
                cfolder += 1
            else:
                directory += emoji + f" <code>{path.name}</code>  <code>{humanbytes(path.stat().st_size)}</code>\n"
                sfile += path.stat().st_size
                cfile += 1
    hfolder, hfile, htotal = (
        humanbytes(sfolder),
        humanbytes(sfile),
        humanbytes(sfolder + sfile),
    )
    directory += f"""
<b>Folders:</b>  <code>{cfolder}</code>  /  <code>{hfolder}</code>
<b>Files:</b>  <code>{cfile}</code>  /  <code>{hfile}</code>
<b>Total:</b>  <code>{cfile + cfolder}</code>  /  <code>{htotal}</code>
"""
    if len(directory) > MAX_MESSAGE_LEN:
        directory = strip_format(directory)
        file = Root / "downloads/ls.txt"
        async with aiofiles.open(file, mode="w") as f:
            await f.write(directory)
        with suppress(BaseException):
            await kst.respond(
                rf"\\**#Getter**// Directory {cat}",
                file=file,
                force_document=True,
                allow_cache=False,
                reply_to=kst.reply_to_msg_id,
                silent=True,
            )
        await yy.try_delete()
        (file).unlink(missing_ok=True)
    else:
        await yy.eor(directory, parse_mode="html")


@kasta_cmd(
    pattern="(shell|sh)(?: |$)((?s).*)",
)
async def _(kst):
    cmd = await kst.client.get_text(kst, group=2)
    if not cmd:
        return await kst.try_delete()
    yy = await kst.eor("`Running...`")
    SHELL_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/shellblacklist.json",
        is_json=True,
        attempts=6,
        fallbacks=DEFAULT_SHELL_BLACKLIST,
    )
    if [_ for _ in cmd.lower().split() if _.startswith(tuple(SHELL_BLACKLIST))] and kst.client.uid not in DEVS:
        return await yy.eod("`Command not allowed.`")
    stdout, stderr, ret, _ = await Runner(cmd)
    icon = "❯" if ret == 0 else "❮"
    shell = f"**{icon}**  ```{cmd}```\n\n"
    err = out = ""
    if stderr:
        err = f"**ERROR:**\n```{stderr}```\n\n"
    if stdout:
        out = f"**OUTPUT:**\n```{stdout}```"
    if not (stderr or stdout):
        out = "**OUTPUT:**\n`success`"
    shell += err + out
    if len(shell) > MAX_MESSAGE_LEN:
        with suppress(BaseException), BytesIO(str.encode(strip_format(shell))) as file:
            file.name = "shell.txt"
            await kst.respond(
                f"`{cmd}`" if len(cmd) < 998 else "Shell Output",
                file=file,
                force_document=True,
                allow_cache=False,
                reply_to=kst.reply_to_msg_id,
                silent=True,
            )
        await yy.try_delete()
        return
    await yy.eor(shell)


@kasta_cmd(
    pattern="devs$",
    for_dev=True,
)
async def _(kst):
    cmds = "**Developer Commands:**\n" + "\n".join(["- {}: {}".format(x, ", ".join(y)) for x, y in DEV_CMDS.items()])
    await kst.sod(cmds)


@kasta_cmd(
    pattern="crash$",
    for_dev=True,
)
@kasta_cmd(
    pattern="crash$",
    dev=True,
)
async def _(kst):
    raise ValueError("not an error, just for testing (>_")


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
        return await kst.eor(str(err), parse_mode=parse_pre)
    await kst.eor("`Downloading Logs...`")
    file = Root / "downloads/getter-heroku.log"
    async with aiofiles.open(file, mode="w") as f:
        await f.write(logs)
    with suppress(BaseException):
        await kst.respond(
            r"\\**#Getter**// Heroku Logs",
            file=file,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await kst.try_delete()
    (file).unlink(missing_ok=True)
    await asyncio.sleep(3)


async def restart_app() -> None:
    with suppress(BaseException):
        import psutil

        proc = psutil.Process(os.getpid())
        for _ in proc.open_files() + proc.connections():
            os.close(_.fd)
    os.execl(sys.executable, sys.executable, "-m", "getter")


plugins_help["dev"] = {
    "{i}alive": "Just showing alive.",
    "{i}uptime|{i}up": "Check current uptime.",
    "{i}ping|ping|Ping": "Check how long it takes to ping.",
    "{i}logs": "Get the full terminal logs.",
    "{i}logs open": "Open logs as text message.",
    "{i}logs carbon": "Get the carbonized terminal logs.",
    "{i}logs heroku": "Get the latest 100 lines of heroku logs.",
    "{i}restart": "Restart the app.",
    "{i}sleep [seconds]/[reply]": "Sleep the bot in few seconds (max 30).",
    "{i}raw [reply]": "Get the raw data of message.",
    "{i}json [reply]": "Raw data with json format.",
    "{i}sysinfo": "Shows System Info.",
    "{i}ls [path]/[reply]": "View all files and folders inside a directory.",
    "{i}shell|{i}sh [command]/[reply]": """Run the linux commands.

**Command Snippets:**
`echo Hello, World!`
`python --version`
`python -c 'import time;print(time.ctime())'`
`cat /etc/os-release`
`uname -a`
`pwd`
`printenv`
`date '+%a, %b %d %Y %T %Z'`
`date +'%A, %B %-d, %Y'`
`ls -lAFh`
`tree`
`df -h`
`du -sh * | sort -hr`
`top -bn1 > output.txt && cat output.txt`
`free -h`
`command -v sh`
`grep -rnliF --color=auto kasta_cmd`
`cat LICENSE`
""",
}
