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
from telethon.tl.functions.help import GetNearestDcRequest
from . import (
    StartTime,
    Root,
    DEVS,
    kasta_cmd,
    plugins_help,
    choice,
    suppress,
    strip_format,
    parse_pre,
    humanbytes,
    time_formatter,
    todict,
    Runner,
    Searcher,
    Carbon,
    MAX_MESSAGE_LEN,
    CARBON_PRESETS,
    DEFAULT_SHELL_BLACKLIST,
    get_blacklisted,
    Hk,
)


@kasta_cmd(
    pattern="dea(c|k)$",
    no_crash=True,
)
async def _(kst):
    yy = "**[Delete Telegram Account](https://telegram.org/deactivate)**"
    await kst.sod(yy)


@kasta_cmd(
    pattern="dc$",
    no_crash=True,
)
async def _(kst):
    dc = await kst.client(GetNearestDcRequest())
    await kst.eor(
        f"**Country:** `{dc.country}`\n"
        f"**Nearest Datacenter:** `{dc.nearest_dc}`\n"
        f"**This Datacenter:** `{dc.this_dc}`",
    )


@kasta_cmd(
    pattern="ping$|([p]ing)$",
    ignore_case=True,
    edited=True,
    no_crash=True,
)
async def _(kst):
    start = time.perf_counter()
    yy = await kst.edit("Ping !")
    end = time.perf_counter()
    speed = end - start
    uptime = time_formatter((time.time() - StartTime) * 1000)
    await yy.edit(
        f"🏓 Pong !!\n<b>Speed</b> - <code>{round(speed, 3)}ms</code>\n<b>Uptime</b> - <code>{uptime}</code>",
        parse_mode="html",
    )


@kasta_cmd(
    pattern=r"haste(?: |$)([\s\S]*)",
)
async def _(kst):
    text = (await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(1)
    if not text:
        await kst.eor("`Provide a text!`", time=5)
        return
    yy = await kst.eor("`Processing...`")
    url = "https://hastebin.com"
    res = await Searcher(
        url=f"{url}/documents",
        post=True,
        data=text.encode("utf-8"),
        re_json=True,
    )
    if not res:
        return await yy.eod("`Try again now!`")
    await yy.eor("{}/{}.txt".format(url, res.get("key")))


@kasta_cmd(
    pattern="logs?(?: |$)(heroku|carbon|open)?",
    no_crash=True,
)
@kasta_cmd(
    pattern="glogs?(?: |$)(heroku|carbon|open)?(?: |$)(.*)",
    no_crash=True,
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    mode = kst.pattern_match.group(1)
    if is_devs:
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
        code = logs = ""
        theme = choice(list(CARBON_PRESETS))
        backgroundColor = CARBON_PRESETS[theme]
        for file in get_terminal_logs():
            async with aiofiles.open(file, mode="r") as f:
                code = await f.read()
            if not code:
                continue
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
                await kst.client.send_file(
                    kst.chat_id,
                    file=logs,
                    caption=r"\\**#Getter**// `Carbon Terminal Logs`",
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id,
                    silent=True,
                )
            (Root / logs).unlink(missing_ok=True)
        await asyncio.sleep(3)
    elif mode == "open":
        logs = ""
        for file in get_terminal_logs():
            async with aiofiles.open(file, mode="r") as f:
                logs = await f.read()
            if not logs:
                continue
            await yy.sod(logs, parse_mode=parse_pre)
        await asyncio.sleep(3)
    else:
        with suppress(BaseException):
            for file in get_terminal_logs():
                await kst.client.send_file(
                    kst.chat_id,
                    file=file,
                    caption=r"\\**#Getter**// `Terminal Logs`",
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id,
                    silent=True,
                )
            await asyncio.sleep(3)


@kasta_cmd(
    pattern="restart$",
    no_crash=True,
)
@kasta_cmd(
    pattern="grestart(?: |$)(.*)",
    no_crash=True,
    own=True,
    senders=DEVS,
)
async def _(kst):
    is_devs = True if not kst.out else False
    if is_devs:
        opt = kst.pattern_match.group(1)
        user_id = None
        with suppress(ValueError):
            user_id = int(opt)
        if user_id and user_id != kst.client.uid:
            return
        await asyncio.sleep(choice((4, 6, 8)))
    yy = await kst.eor("`Restarting...`", silent=True)
    os.system("clear")
    await asyncio.sleep(1)
    await yy.eor(r"\\**#Getter**// `Restarting... Wait for a few minutes.`")
    if not Hk.is_heroku:
        await restart_app()
        return
    try:
        app = Hk.heroku().app(Hk.name)
        app.restart()
    except Exception as err:
        reply = await yy.eor(f"**ERROR:**\n`{err}`")
        await reply.reply(r"\\**#Getter**// `Restarting as locally...`", silent=True)
        await restart_app()


@kasta_cmd(
    pattern="sleep(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    sec = kst.pattern_match.group(1)
    counter = int(sec) if sec.replace(".", "", 1).isdecimal() else 5
    counter = 5 if counter > 50 else counter
    await kst.eor("`Sleep...`")
    time.sleep(counter)
    await kst.eor("`wake-up`", time=5)


@kasta_cmd(
    pattern="(raw|json)$",
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    msg = await kst.get_reply_message() if kst.is_reply else kst
    if match == "json":
        text = json.dumps(todict(msg), indent=2, default=str, sort_keys=False)
    else:
        text = f"{msg.stringify()}"
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
    info = ""
    async with aiofiles.open(file, mode="r") as f:
        info = await f.read()
    if not info:
        return await yy.try_delete()
    theme = choice(list(CARBON_PRESETS))
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
        await kst.client.send_file(
            kst.chat_id,
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
    cat = kst.pattern_match.group(1)
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
    _symlinks = []
    _folders = []
    _shells = []
    _dockers = []
    _pyfiles = []
    _jsons = []
    _texts = []
    _audios = []
    _videos = []
    _pics = []
    _apks = []
    _exes = []
    _archives = []
    _books = []
    _others = []
    _otherfiles = []
    for p in paths:
        if p.is_symlink():
            _symlinks.append(("🔗", p))
        elif p.is_dir():
            _folders.append(("📂", p))
        elif "docker" in str(p).lower():
            _dockers.append(("🐋", p))
        elif p.suffix in (".sh", ".bash", ".zsh", ".fish"):
            _shells.append(("💻", p))
        elif p.suffix == ".py":
            _pyfiles.append(("🐍", p))
        elif p.suffix in (".json", ".ini", ".cfg", ".yml", ".yaml", ".toml", ".csv"):
            _jsons.append(("🔮", p))
        elif p.suffix in (".txt", ".text", ".log"):
            _texts.append(("📃", p))
        elif p.suffix in (".mp3", ".ogg", ".m4a", ".opus", ".flac", ".wav"):
            _audios.append(("🔊", p))
        elif p.suffix in (".mkv", ".mp4", ".avi", ".gif", "webm", ".mov", ".flv"):
            _videos.append(("🎥", p))
        elif p.suffix in (".jpg", ".jpeg", ".png", ".svg", ".webp", ".bmp", ".ico"):
            _pics.append(("🖼", p))
        elif p.suffix in (".apk", ".xapk", ".apks", ".sapk"):
            _apks.append(("📲", p))
        elif p.suffix in (".exe", ".iso"):
            _exes.append(("⚙", p))
        elif p.suffix in (
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".bz2",
            ".xz",
            ".lz4",
            ".zst",
        ):
            _archives.append(("🗜", p))
        elif p.suffix in (".pdf", ".epub", ".doc"):
            _books.append(("📚", p))
        elif p.is_file():
            _others.append(("🏷️", p))
        else:
            _otherfiles.append(("📒", p))
    lists = [
        *sorted(_symlinks),
        *sorted(_folders),
        *sorted(_shells),
        *sorted(_dockers),
        *sorted(_pyfiles),
        *sorted(_jsons),
        *sorted(_texts),
        *sorted(_audios),
        *sorted(_videos),
        *sorted(_pics),
        *sorted(_apks),
        *sorted(_exes),
        *sorted(_archives),
        *sorted(_books),
        *sorted(_others),
        *sorted(_otherfiles),
    ]
    directory = ""
    sfile, sfolder = 0, 0
    cfile, cfolder = 0, 0
    for emoji, path in lists:
        with suppress(BaseException):
            if path.is_dir():
                size = 0
                for p in path.rglob("*"):
                    size += p.stat().st_size
                directory += emoji + f" <code>{path.name}</code>" + "  <code>" + humanbytes(size) + "</code>\n"
                sfolder += size
                cfolder += 1
            else:
                directory += (
                    emoji + f" <code>{path.name}</code>" + "  <code>" + humanbytes(path.stat().st_size) + "</code>\n"
                )
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
            caption = rf"\\**#Getter**// `Directory {cat}`"
            await kst.client.send_file(
                kst.chat_id,
                file=file,
                caption=caption,
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
    pattern=r"(shell|sh)(?: |$)([\s\S]*)",
)
async def _(kst):
    cmd = kst.pattern_match.group(2)
    if not cmd:
        return await kst.try_delete()
    yy = await kst.eor("`Running...`")
    SHELL_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/shellblacklist.json",
        is_json=True,
        attempts=6,
        fallbacks=DEFAULT_SHELL_BLACKLIST,
    )
    if bool([x for x in cmd.lower().split() if x.startswith(tuple(SHELL_BLACKLIST))]) and kst.client.uid not in DEVS:
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
        shell = strip_format(shell)
        with suppress(BaseException):
            with BytesIO(str.encode(shell)) as file:
                file.name = "shell.txt"
                caption = f"`{cmd}`" if len(cmd) < 998 else "`Shell Output`"
                await kst.client.send_file(
                    kst.chat_id,
                    file=file,
                    caption=rf"\\**#Getter**// {caption}",
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id,
                    silent=True,
                )
        await yy.try_delete()
        return
    await yy.eor(shell)


@kasta_cmd(
    pattern="crash$",
)
async def _(kst):
    await kst.try_delete()
    raise ValueError("not an error, just for testing (>_")


def get_terminal_logs():
    return sorted((Root / "logs").rglob("getter-*.log"))


async def heroku_logs(kst) -> None:
    if not Hk.api:
        await kst.eor("Please set `HEROKU_API` in Config Vars.")
        return
    if not Hk.name:
        await kst.eor("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        app = Hk.heroku().app(Hk.name)
        logs = app.get_log(lines=100)
    except Exception as err:
        await kst.eor(f"**ERROR:**\n`{err}`")
        return
    await kst.eor("`Downloading Logs...`")
    file = "getter-heroku.log"
    async with aiofiles.open(file, mode="w") as f:
        await f.write(logs)
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            caption=r"\\**#Getter**// `Heroku Logs`",
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
    await kst.try_delete()
    (Root / file).unlink(missing_ok=True)
    await asyncio.sleep(3)


async def restart_app() -> None:
    import psutil

    with suppress(BaseException):
        proc = psutil.Process(os.getpid())
        for p in proc.open_files() + proc.connections():
            os.close(p.fd)
    os.execl(sys.executable, sys.executable, "-m", "getter")


plugins_help["dev"] = {
    "{i}deak|{i}deac": "Give a link Deactivated Account.",
    "{i}dc": "Finds the nearest datacenter from your server.",
    "{i}ping|ping|Ping": "Check response time.",
    "{i}haste <text/reply>": "Upload text to hastebin.",
    "{i}logs": "Get the full terminal logs.",
    "{i}logs open": "Open logs as text message.",
    "{i}logs carbon": "Get the carbonized terminal logs.",
    "{i}logs heroku": "Get the latest 100 lines of heroku logs.",
    "{i}restart": "Restart the app.",
    "{i}sleep <time/in seconds>": "Sleep the bot in few seconds (max 50).",
    "{i}raw <reply>": "Get the raw data of message.",
    "{i}json <reply>": "Same as above but with json format.",
    "{i}sysinfo": "Shows System Info.",
    "{i}ls <path>": "View all files and folders inside a directory.",
    "{i}shell|{i}sh <cmds>": """Run the linux commands.
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
`cat LICENSE`""",
}
