# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
import html
import json
import os
import sys
import time
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from aiofiles import open as aiopen
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from telethon import functions
from validators.url import url
from . import (
    choice,
    StartTime,
    Root,
    Var,
    DEVS,
    HELP,
    kasta_cmd,
    display_name,
    strip_format,
    humanbytes,
    time_formatter,
    get_doc_mime,
    Runner,
    Carbon,
    MAX_MESSAGE_LEN,
    CARBON_PRESETS,
    RAYSO_THEMES,
    DEFAULT_SHELL_BLACKLIST,
    get_blacklisted,
    Heroku,
    CHROME_BIN,
    CHROME_DRIVER,
)


@kasta_cmd(
    pattern="dea(c|k)$",
)
async def _(kst):
    msg = "**[Delete Telegram Account](https://telegram.org/deactivate)**"
    await kst.sod(msg)


@kasta_cmd(
    pattern="dc$",
)
async def _(kst):
    res = await kst.client(functions.help.GetNearestDcRequest())
    await kst.eor(
        f"**Country:** `{res.country}`\n"
        f"**Nearest Datacenter:** `{res.nearest_dc}`\n"
        f"**This Datacenter:** `{res.this_dc}`",
    )


@kasta_cmd(
    pattern="ping$|([p]ing)$",
    ignore_case=True,
    edited=True,
    no_crash=True,
)
async def _(kst):
    start = time.perf_counter()
    msg = await kst.edit("Ping !")
    end = time.perf_counter()
    speed = end - start
    uptime = time_formatter((time.time() - StartTime) * 1000)
    await msg.edit(
        f"🏓 Pong !!\n<b>Speed</b> - <code>{round(speed, 3)}ms</code>\n<b>Uptime</b> - <code>{uptime}</code>",
        parse_mode="html",
    )


@kasta_cmd(
    pattern="logs?(?: |$)(heroku|hk|h|carbon|open)?",
    no_crash=True,
)
@kasta_cmd(
    pattern="glogs?(?: |$)(heroku|hk|h|carbon|open)?(?: |$)(.*)",
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
        try:
            user_id = int(opt)
        except ValueError:
            pass
        if user_id and user_id != kst.client.uid:
            return
        await asyncio.sleep(choice((4, 6, 8)))
    msg = await kst.eor("`Getting...`", silent=True)
    if mode in ("heroku", "hk", "h"):
        return await heroku_logs(msg)
    else:
        await asyncio.sleep(3)
        await msg.try_delete()
    if mode == "carbon":
        code = logs = ""
        theme, backgroundColor = choice(CARBON_PRESETS)
        for file in get_terminal_logs():
            async with aiopen(file, mode="r") as f:
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
                    silent=True,
                )
                await asyncio.sleep(3)
            (Root / logs).unlink(missing_ok=True)
    elif mode == "open":
        logs = ""
        for file in get_terminal_logs():
            async with aiopen(file, mode="r") as f:
                logs = await f.read()
            if not logs:
                continue
            await msg.sod(f"`{logs}`")
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
        try:
            user_id = int(opt)
        except ValueError:
            pass
        if user_id and user_id != kst.client.uid:
            return
        await asyncio.sleep(choice((4, 6, 8)))
    msg = await kst.eor("`Restarting...`", silent=True)
    os.system("clear")
    await asyncio.sleep(1)
    await msg.eor(r"\\**#Getter**// `Restarting... Wait for a few minutes.`")
    if not (Var.HEROKU_API and Var.HEROKU_APP_NAME):
        await restart_app()
        return
    try:
        heroku_conn = Heroku()
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
        app.restart()
    except Exception as err:
        rep = await msg.eor(f"**ERROR:**\n`{err}`")
        await rep.reply(r"\\**#Getter**// `Restarting as locally...`", silent=True)
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
    pattern="raw(?: |$)(.*)",
    no_crash=True,
)
async def _(kst):
    match = kst.pattern_match.group(1)
    msg = await kst.get_reply_message() if kst.is_reply else kst
    if match == "json":
        text = json.dumps(todict(msg), indent=2, default=str, sort_keys=False)
    else:
        text = f"{msg.stringify()}"
    if len(text) > MAX_MESSAGE_LEN:
        with suppress(BaseException):
            with BytesIO(str.encode(text)) as file:
                file.name = f"raw_output.txt"
                await kst.client.send_file(
                    kst.chat_id,
                    file=file,
                    caption=r"\\**#Getter**// `Message Raw Data`",
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id or kst.id,
                    silent=True,
                )
        await kst.try_delete()
    else:
        await kst.eor(f"<pre>{html.escape(text)}</pre>", parse_mode="html")


@kasta_cmd(
    pattern=r"carbon(?: |$)([\s\S]*)",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if kst.is_reply:
        rep = await kst.get_reply_message()
        if rep.media and bool([x for x in ("text", "application") if x in get_doc_mime(rep.media)]):
            file = await kst.client.download_media(rep)
            code = None
            async with aiopen(file, mode="r") as f:
                code = await f.read()
            if not code:
                return await msg.try_delete()
            (Root / file).unlink(missing_ok=True)
        else:
            code = rep.message
    else:
        code = kst.pattern_match.group(1)
    if not code:
        return await msg.eod("`Reply to text message or readable file.`")
    theme, backgroundColor = choice(CARBON_PRESETS)
    windowTheme = choice(("none", "sharp", "bw"))
    carbon = await Carbon(
        code.strip(),
        file_name="carbon",
        download=True,
        fontFamily="Fira Code",
        theme=theme,
        backgroundColor=backgroundColor,
        dropShadow=True if windowTheme != "bw" else False,
        windowTheme=windowTheme,
    )
    if not carbon:
        return await msg.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=carbon,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id or kst.id,
            silent=True,
        )
    await msg.try_delete()
    (Root / carbon).unlink(missing_ok=True)


@kasta_cmd(
    pattern="rayso",
    no_crash=True,
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    opts = kst.text.split()
    theme, dark, text = None, True, None
    if len(opts) > 2:
        if opts[1] in RAYSO_THEMES:
            theme = opts[1]
        dark = opts[2].lower().strip() in ["true", "t"]
    elif len(opts) > 1:
        if opts[1] in RAYSO_THEMES:
            theme = opts[1]
        elif opts[1] == "list":
            text = "**List of Rayso Themes:**\n" + "\n".join([f"- `{th}`" for th in RAYSO_THEMES])
            await msg.eor(text)
            return
        else:
            with suppress(BaseException):
                text = kst.text.split(maxsplit=1)[1]
    if not theme:
        theme = choice(RAYSO_THEMES)
    if kst.is_reply:
        rep = await kst.get_reply_message()
        text = rep.text
        from_user = rep.sender
    else:
        from_user = await kst.client.get_entity("me")
    title = display_name(from_user)
    rayso = await Carbon(
        text,
        download=True,
        rayso=True,
        title=title,
        theme=theme,
        darkMode=dark,
    )
    if not rayso:
        return await msg.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=rayso,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id or kst.id,
            silent=True,
        )
    await msg.try_delete()
    (Root / rayso).unlink(missing_ok=True)


@kasta_cmd(
    pattern="sysinfo$",
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    file = "neofetch.txt"
    (Root / file).unlink(missing_ok=True)
    _, _, ret, _ = await Runner(f"neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g'>>{file}")
    if ret != 0:
        return await msg.try_delete()
    info = ""
    async with aiopen(file, mode="r") as f:
        info = await f.read()
    if not info:
        return await msg.try_delete()
    theme, backgroundColor = choice(CARBON_PRESETS)
    neofetch = await Carbon(
        info.replace("\n\n", "").strip(),
        file_name="neofetch",
        fontFamily="Hack",
        theme=theme,
        backgroundColor=backgroundColor,
        dropShadow=True,
    )
    if not neofetch:
        return await msg.try_delete()
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=neofetch,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id or kst.id,
            silent=True,
        )
    await msg.try_delete()
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
    msg = await kst.eor("`Loading...`")
    try:
        paths = sorted(Path(".").glob(cat))
    except BaseException:
        paths = None
    if not paths:
        return await msg.eor("`No such directory or empty or incorrect.`", time=5)
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
        try:
            if path.is_dir():
                size = 0
                for p in path.rglob("*"):
                    size += p.stat().st_size
                directory += emoji + f" `{path.name}`" + "  `" + humanbytes(size) + "`\n"
                sfolder += size
                cfolder += 1
            else:
                directory += emoji + f" `{path.name}`" + "  `" + humanbytes(path.stat().st_size) + "`\n"
                sfile += path.stat().st_size
                cfile += 1
        except BaseException:
            pass
    hfolder, hfile, htotal = (
        humanbytes(sfolder),
        humanbytes(sfile),
        humanbytes(sfolder + sfile),
    )
    directory += f"""
**Folders:**  `{cfolder}`  /  `{hfolder}`
**Files:**  `{cfile}`  /  `{hfile}`
**Total:**  `{cfile + cfolder}`  /  `{htotal}`
"""
    if len(directory) > MAX_MESSAGE_LEN:
        directory = strip_format(directory)
        file = "directory_output.txt"
        async with aiopen(file, mode="w") as f:
            await f.write(directory)
        with suppress(BaseException):
            await kst.client.send_file(
                kst.chat_id,
                file=file,
                caption=rf"\\**#Getter**// `Directory {cat}`",
                force_document=True,
                allow_cache=False,
                reply_to=kst.reply_to_msg_id or kst.id,
                silent=True,
            )
        await msg.try_delete()
        (Root / file).unlink(missing_ok=True)
    else:
        await msg.eor(directory)


@kasta_cmd(
    pattern="ss(?: |$)(.*)",
)
async def _(kst):
    to_ss = kst.pattern_match.group(1)
    if not to_ss:
        return await kst.try_delete()
    msg = await kst.eor("`Processing...`")
    start_time = time.time()
    toss = to_ss
    urlss = url(toss)
    if not urlss:
        toss = f"http://{to_ss}"
        urlss = url(toss)
    if not urlss:
        return await msg.eod("`Input is not supported url.`")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--test-type")
    options.add_argument("--disable-logging")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    )
    options.binary_location = CHROME_BIN
    msg = await msg.eor("`Taking Screenshot...`")
    service = ChromeService(executable_path=CHROME_DRIVER)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(toss)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
    )
    driver.set_window_size(width + 100, height + 100)
    ss_png = driver.get_screenshot_as_png()
    msg = await msg.eor("`Screenshot Taked...`")
    driver.close()
    taken = time_formatter((time.time() - start_time) * 1000)
    with suppress(BaseException):
        with BytesIO(ss_png) as file:
            file.name = f"{to_ss}.png"
            caption = rf"""\\**#Getter**//
**URL:** `{to_ss}`
**Taken:** `{taken}`"""
            await kst.client.send_file(
                kst.chat_id,
                file=file,
                caption=caption,
                force_document=True,
                allow_cache=False,
                reply_to=kst.reply_to_msg_id or kst.id,
                silent=True,
            )
    driver.quit()
    await msg.try_delete()


@kasta_cmd(
    pattern=r"(shell|sh)(?: |$)([\s\S]*)",
)
async def _(kst):
    cmd = kst.pattern_match.group(2)
    if not cmd:
        return await kst.try_delete()
    msg = await kst.eor("`Running...`")
    SHELL_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/shellblacklist.json",
        is_json=True,
        attempts=6,
        fallbacks=DEFAULT_SHELL_BLACKLIST,
    )
    if bool([x for x in cmd.lower().split() if x.startswith(tuple(SHELL_BLACKLIST))]) and kst.client.uid not in DEVS:
        return await msg.eod("`Command not allowed.`")
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
                file.name = "shell_output.txt"
                caption = f"`{cmd}`" if len(cmd) < 998 else "`Shell Output`"
                await kst.client.send_file(
                    kst.chat_id,
                    file=file,
                    caption=rf"\\**#Getter**// {caption}",
                    force_document=True,
                    allow_cache=False,
                    reply_to=kst.reply_to_msg_id or kst.id,
                    silent=True,
                )
        await msg.try_delete()
    else:
        await msg.eor(shell)


def get_terminal_logs():
    return sorted((Root / "logs").rglob("getter-*.log"))


async def heroku_logs(kst) -> None:
    if not Var.HEROKU_API:
        await kst.eor("Please set `HEROKU_API` in Config Vars.")
        return
    if not Var.HEROKU_APP_NAME:
        await kst.eor("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        heroku_conn = Heroku()
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
        logs = app.get_log()
    except Exception as err:
        await kst.eor(f"**ERROR:**\n`{err}`")
        return
    await kst.eor("`Downloading Logs...`")
    file = "getter-heroku.log"
    async with aiopen(file, mode="w") as f:
        await f.write(logs)
    with suppress(BaseException):
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            caption=r"\\**#Getter**// `Heroku Logs`",
            force_document=True,
            allow_cache=False,
            silent=True,
        )
    await kst.try_delete()
    (Root / file).unlink(missing_ok=True)


async def restart_app() -> None:
    import psutil

    with suppress(BaseException):
        proc = psutil.Process(os.getpid())
        for p in proc.open_files() + proc.connections():
            os.close(p.fd)
    os.execl(sys.executable, sys.executable, "-m", "getter")


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(  # noqa: C404
            [
                (key, todict(val, classkey))
                for key, val in obj.__dict__.items()
                if not callable(val) and not key.startswith("_")
            ]
        )
        if classkey and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


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

❯ `{i}logs open`
Open logs as text message.

❯ `{i}logs carbon`
Get the carbonized terminal logs.

❯ `{i}logs <heroku|hk|h>`
Get the latest 100 lines of heroku logs.

❯ `{i}restart`
Restart the app.

❯ `{i}sleep <time/in seconds>`
Sleep the bot in few seconds (max 50).

❯ `{i}raw <json> <reply>`
Get the raw data of message.

❯ `{i}carbon <text/reply>`
Carbonise the text with random presets.

❯ `{i}rayso <theme> <text/reply>`
Beauty showcase the text by rayso.

❯ `{i}rayso list`
Get list of rayso themes.

❯ `{i}sysinfo`
Shows System Info.

❯ `{i}ls <path>`
View all files and folders inside a directory.

❯ `{i}ss <link>`
Take a full screenshot of a website.

❯ `{i}shell|{i}sh <cmds>`
Run the linux commands.

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
        ]
    }
)
