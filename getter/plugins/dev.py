# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import sys
from io import BytesIO, StringIO
from json import dumps
from pathlib import Path
from random import choice
from traceback import format_exc

import aiofiles
from telethon.tl import functions, types

from . import (
    CARBON_PRESETS,
    DEFAULT_SHELL_BLACKLIST,
    DEV_CMDS,
    DEVS,
    LSFILES_MAP,
    MAX_MESSAGE_LEN,
    Carbon,
    Root,
    Runner,
    formatx_send,
    get_blacklisted,
    getter_app,
    humanbytes,
    kasta_cmd,
    parse_pre,
    plugins_help,
    strip_format,
    to_dict,
)

fun = functions
typ = types
bot = getter_app


@kasta_cmd(
    pattern="(raw|json)$",
)
async def _(kst):
    mode = kst.pattern_match.group(1)
    msg = await kst.get_reply_message() if kst.is_reply else kst
    if mode == "json":
        text = dumps(
            to_dict(msg),
            indent=1,
            default=str,
            sort_keys=False,
            ensure_ascii=False,
        )
    else:
        text = msg.stringify()
    await kst.eor(text, parts=True, parse_mode=parse_pre)


@kasta_cmd(
    pattern="sysinfo$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    file = "downloads/neofetch.txt"
    _, _, ret, _ = await Runner(f"neofetch|sed 's/\x1b\\[[0-9;\\?]*[a-zA-Z]//g'>>{file}")
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
    await yy.eor(
        file=neofetch,
        force_document=False,
    )
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
    symlinks, folders, dockers, allfiles = [], [], [], []
    for p in paths:
        if p.is_symlink():
            symlinks.append(("🔗", p))
        elif p.is_dir():
            folders.append(("📂", p))
        elif "docker" in str(p).lower():
            dockers.append(("🐋", p))
        else:
            for x in LSFILES_MAP:
                if p.suffix in x:
                    allfiles.append((LSFILES_MAP[x], p))
                    break
            else:
                if p.is_file():
                    allfiles.append(("🏷️", p))
                else:
                    allfiles.append(("📒", p))
    lists = [
        *sorted(folders),
        *sorted(symlinks),
        *sorted(allfiles),
        *sorted(dockers),
    ]
    directory = ""
    sfile, sfolder, cfile, cfolder = 0, 0, 0, 0
    for emoji, path in lists:
        try:
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
        except BaseException:
            pass
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
        await yy.eor(
            rf"\\**#Getter**// Directory {cat}",
            file=file,
            force_document=True,
        )
        (file).unlink(missing_ok=True)
    else:
        await yy.eor(directory, parse_mode="html")


@kasta_cmd(
    pattern=r"eval(?: |$)([\s\S]*)",
)
async def _(kst):
    code = await kst.client.get_text(kst)
    if not code:
        return await kst.try_delete()
    yy = await kst.eor("`Evaluating...`")
    try:
        out = eval(code)
        result = f"<b>Evaluate:</b>\n<pre>{code}</pre>\n\n"
        result += f"<b>Result</b>:\n<pre>{out}</pre>"
        await yy.sod(result, parse_mode="html")
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern=r"exec(?: |$)([\s\S]*)",
)
@kasta_cmd(
    pattern=r"exec(?: |$)([\s\S]*)",
    dev=True,
)
async def _(kst):
    code = await kst.client.get_text(kst)
    if not code:
        return await kst.try_delete()
    yy = await kst.eor("`Executing...`")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        value = await aexec(code, kst)
    except BaseException:
        value = None
        exc = format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    execute = exc or stderr or stdout or _parse_eval(value) or "Success"
    result = f"<b>Execute:</b>\n<pre>{code}</pre>\n\n"
    result += f"<b>Result:</b>\n<pre>{execute}</pre>"
    if len(result) > MAX_MESSAGE_LEN:
        with BytesIO(str.encode(strip_format(result))) as file:
            file.name = "exec.txt"
            await yy.eor(
                f"<pre>{code}</pre>",
                file=file,
                force_document=True,
                parse_mode="html",
            )
        return
    await yy.sod(result, parse_mode="html")


@kasta_cmd(
    pattern=r"(shell|sh)(?: |$)([\s\S]*)",
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
    if any(_.startswith(tuple(SHELL_BLACKLIST)) for _ in cmd.lower().split()) and kst.client.uid not in DEVS:
        return await yy.eod("`Command not allowed.`")
    stdout, stderr, ret, _ = await Runner(cmd)
    icon = "❯" if ret == 0 else "❮"
    result = f"<b>{icon}</b>  <pre>{cmd}</pre>\n\n"
    err, out = "", ""
    if stderr:
        err = f"<b>Error:</b>\n<pre>{stderr}</pre>\n\n"
    if stdout:
        out = f"<b>Result:</b>\n<pre>{stdout}</pre>"
    if not stderr and not stdout:
        out = "<b>Result:</b>\n<code>success</code>"
    result += err + out
    if len(result) > MAX_MESSAGE_LEN:
        with BytesIO(str.encode(strip_format(result))) as file:
            file.name = "shell.txt"
            await yy.eor(
                f"<pre>{cmd}</pre>",
                file=file,
                force_document=True,
                parse_mode="html",
            )
        return
    await yy.sod(result, parse_mode="html")


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
async def _(kst):  # noqa: RUF029
    raise ValueError("not an error, just for testing (>_")


def _parse_eval(value=None):
    if not value:
        return value
    if hasattr(value, "stringify"):
        try:
            return value.stringify()
        except TypeError:
            pass
    elif isinstance(value, dict):
        try:
            return dumps(value, indent=1, ensure_ascii=False)
        except BaseException:
            pass
    return str(value)


def _stringify(text=None, *args, **kwargs):
    if text:
        text = _parse_eval(text)
    return print(text, *args, **kwargs)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n print = p = _stringify"
            + "\n kst = message = event = e"
            + "\n reply = await event.get_reply_message()"
            + "\n chat = event.chat_id"
        )
        + "".join(f"\n {_}" for _ in code.split("\n"))
    )
    return await locals()["__aexec"](event, event.client)


plugins_help["dev"] = {
    "{i}raw [reply]": "Get the raw data of message object.",
    "{i}json [reply]": "Raw data with json format.",
    "{i}sysinfo": "Shows System Info.",
    "{i}ls [path]/[reply]": "View all files and folders inside a directory.",
    "{i}eval [code]/[reply]": "Evaluate Python code.",
    "{i}exec [code]/[reply]": """Execute Python code.
**Exec Shortcuts:**
`fun = telethon.tl.functions`
`typ = telethon.tl.types`
`client = bot = event.client`
`message = e = event`
`p = print`
`reply = await event.get_reply_message()`
`chat = event.chat_id`
""",
    "{i}shell|{i}sh [command]/[reply]": """Run the linux commands.
**Shell Command Snippets:**
`echo Hello, World!`
`python3 --version`
`python3 -c 'import time;print(time.ctime())'`
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
