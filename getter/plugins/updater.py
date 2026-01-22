# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import os
from datetime import UTC, datetime
from random import choice
from sys import executable

import aiofiles
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from . import (
    MAX_MESSAGE_LEN,
    TZ,
    Root,
    Runner,
    Var,
    __layer__,
    __pyversion__,
    __tlversion__,
    __version__,
    formatx_send,
    get_random_hex,
    gvar,
    hk,
    hl,
    humanbool,
    kasta_cmd,
    plugins_help,
    sgvar,
    strip_format,
)

_UPDATE_LOCK = asyncio.Lock()
UPSTREAM_REPO = "https://github.com/kastaid/getter.git"
UPSTREAM_BRANCH = "main"
help_text = f"""
❯ `{hl}update [now/pull]`
Temporarily update as locally.

❯ `{hl}update [deploy/push]`
Permanently update as heroku.

❯ `{hl}update force`
Force temporarily update as locally.
"""
test_text = """
├  <b>User:</b> <code>{}</code>
├  <b>ID:</b> <code>{}</code>
├  <b>Getter Version:</b> <code>{}</code>
├  <b>Python Version:</b> <code>{}</code>
├  <b>Telethon Version:</b> <code>{}</code>
├  <b>Telegram Layer:</b> <code>{}</code>
├  <b>Handler:</b> <code>{}</code>
├  <b>Sudo:</b> <code>{}</code>
├  <b>PM-Guard:</b> <code>{}</code>
├  <b>PM-Logs:</b> <code>{}</code>
├  <b>PM-Block:</b> <code>{}</code>
├  <b>Anti-PM:</b> <code>{}</code>
├  <b>Heroku App:</b> <code>{}</code>
├  <b>Heroku Stack:</b> <code>{}</code>
├  <b>Uptime:</b> <code>{}</code>
├  <b>UTC Now:</b> <code>{}</code>
└  <b>Local Now:</b> <code>{}</code>
"""


@kasta_cmd(
    pattern="update(?: |$)(force|now|deploy|pull|push)?(?: |$)(.*)",
)
@kasta_cmd(
    pattern="getterup(?: |$)(force|now|deploy|pull|push)?(?: |$)(.*)",
    edited=True,
    dev=True,
)
async def _(kst):
    if not kst.is_dev and _UPDATE_LOCK.locked():
        return await kst.eor("`Please wait until previous •update• finished...`", time=5, silent=True)
    async with _UPDATE_LOCK:
        group = kst.pattern_match.group
        mode, opt, is_force, is_now, is_deploy, state = group(1), group(2), False, False, False, ""
        if not Var.DEV_MODE and mode == "force":
            is_force = True
            state = "[FORCE] "
        elif mode in {"now", "pull"}:
            is_now = True
            state = "[NOW] "
        elif mode in {"deploy", "push"}:
            is_deploy = True
            state = "[DEPLOY] "
        else:
            state = "[CHECK] "
        if kst.is_dev and opt:
            user_id = version = None
            try:
                user_id = int(opt)
            except ValueError:
                version = opt
            if not version and user_id != kst.client.uid:
                return
            if not user_id and version == __version__:
                return
        if kst.is_dev:
            await asyncio.sleep(choice((5, 7, 9)))
        yy = await kst.eor(f"`{state}Fetching...`", silent=True)
        try:
            repo = Repo()
        except NoSuchPathError as err:
            return await yy.eor(f"`{state}Directory not found : {err}`")
        except GitCommandError as err:
            return await yy.eor(f"`{state}Early failure : {err}`")
        except InvalidGitRepositoryError:
            repo = Repo.init()
            origin = repo.create_remote("origin", UPSTREAM_REPO)
            origin.fetch()
            repo.create_head("main", origin.refs.main)
            repo.heads.main.set_tracking_branch(origin.refs.main)
            repo.heads.main.checkout(True)
        await Runner(f"git fetch origin {UPSTREAM_BRANCH}")
        if is_deploy:
            if kst.is_dev:
                await asyncio.sleep(5)
            await yy.eor(f"`{state}Updating ~ Please Wait...`")
            return await Pushing(yy, state, repo)
        try:
            verif = verify(repo, f"HEAD..origin/{UPSTREAM_BRANCH}")
        except BaseException:
            verif = None
        if not (verif or is_force):
            return await yy.eor(rf"\\**#Getter**// `v{__version__} up-to-date as {UPSTREAM_BRANCH}`")
        if not (mode or is_force):
            changelog = generate_changelog(repo, f"HEAD..origin/{UPSTREAM_BRANCH}")
            return await show_changelog(yy, changelog)
        if is_force:
            await asyncio.sleep(3)
        if is_now or is_force:
            await yy.eor(f"`{state}Updating ~ Please Wait...`")
            await Pulling(yy, state)
        return


@kasta_cmd(
    pattern="repo$",
)
async def _(kst):
    await kst.eor(
        "https://github.com/kastaid/getter",
        link_preview=True,
    )


@kasta_cmd(
    pattern="test$",
)
@kasta_cmd(
    pattern="test$",
    sudo=True,
)
@kasta_cmd(
    pattern="gtest(?: |$)(.*)",
    edited=True,
    dev=True,
)
async def _(kst):
    ga = kst.client
    clean = False
    if kst.is_dev:
        opt = kst.pattern_match.group(1)
        if opt:
            user_id = version = None
            try:
                user_id = int(opt)
            except ValueError:
                version = opt
            if not version and user_id != ga.uid:
                return
            if not user_id and version == __version__:
                return
            clean = True
        if not clean:
            await asyncio.sleep(choice((4, 6, 8)))
    if kst.is_sudo:
        await asyncio.sleep(choice((4, 6, 8)))
    # http://www.timebie.com/std/utc
    utc_now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    local_now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    yy = await kst.eor("`Processing...`", silent=True, force_reply=True)
    await yy.eor(
        test_text.format(
            ga.full_name,
            ga.uid,
            __version__,
            __pyversion__,
            __tlversion__,
            __layer__,
            hl,
            humanbool(await gvar("_sudo", use_cache=True), toggle=True),
            humanbool(await gvar("_pmguard", use_cache=True), toggle=True),
            humanbool(await gvar("_pmlog", use_cache=True), toggle=True),
            humanbool(await gvar("_pmblock", use_cache=True), toggle=True),
            humanbool(await gvar("_antipm", use_cache=True), toggle=True),
            hk.name or "none",
            hk.stack,
            ga.uptime,
            utc_now,
            local_now,
        ),
        parse_mode="html",
        time=20 if clean else 0,
    )


async def ignores() -> None:
    rems = " ".join(
        [
            ".github",
            "docs",
            "README.md",
        ]
    )
    backup_dir = Root / "backup/" / get_random_hex()
    await Runner(f"mkdir -p {backup_dir} && mv -f {rems} -t {backup_dir}")


async def update_packages() -> None:
    reqs = Root / "requirements.txt"
    await Runner(f"{executable} -m pip install --disable-pip-version-check --default-timeout=100 -r {reqs}")


async def force_pull() -> None:
    await Runner(f"git pull --force && git reset --hard origin/{UPSTREAM_BRANCH}")


async def force_push() -> str:
    push = f"git push --force https://heroku:{hk.api}@git.heroku.com/{hk.name}.git HEAD:main"
    _, err, _, _ = await Runner(push)
    return err


def verify(repo, diff) -> bool:
    v = ""
    for c in repo.iter_commits(diff):
        v = str(c.count())
    return bool(v)


def generate_changelog(repo, diff) -> str:
    chlog = ""
    rep = UPSTREAM_REPO.replace(".git", "")
    ch = rf"\\<b>#Getter</b>// <b>v{__version__} New UPDATE available for <a href={rep}/tree/{UPSTREAM_BRANCH}>[{UPSTREAM_BRANCH}]</a>:</b>"
    date = "%Y-%m-%d %H:%M:%S"
    for _ in repo.iter_commits(diff):
        chlog += f"\n\n<b>#{_.count()}</b> [<code>{_.committed_datetime.strftime(date)}</code>]\n<code>{_.hexsha}</code>\n<b><a href={rep.rstrip('/')}/commit/{_}>[{_.summary}]</a></b> ~ <code>{_.author}</code>"
    if chlog:
        return str(ch + chlog)
    return chlog


async def show_changelog(kst, changelog) -> None:
    if len(changelog) > MAX_MESSAGE_LEN:
        changelog = strip_format(changelog)
        file = Root / "downloads/changelog.txt"
        async with aiofiles.open(file, mode="w") as f:
            await f.write(changelog)
        try:
            chlog = await kst.eor(
                r"\\**#Getter**// View this file to see changelog.",
                file=file,
                force_document=True,
            )
        except Exception as err:
            chlog = await kst.eor(formatx_send(err), parse_mode="html")
        (file).unlink(missing_ok=True)
    else:
        chlog = await kst.eor(changelog, parse_mode="html")
    await chlog.reply(help_text, silent=True)


async def Pulling(kst, state) -> None:
    if not Var.DEV_MODE:
        await force_pull()
        # await ignores()
        await update_packages()
    up = rf"""\\**#Getter**// `{state}Updated Successfully...`
Wait for a few seconds, then run `{hl}ping` command."""
    yy = await kst.eor(up)
    try:
        chat_id = yy.chat_id or yy.from_id
        await sgvar("_restart", f"{chat_id}|{yy.id}")
    except BaseException:
        pass
    try:
        import psutil

        proc = psutil.Process(os.getpid())
        for _ in proc.open_files() + proc.connections():
            os.close(_.fd)
    except BaseException:
        pass
    os.execl(executable, executable, "-m", "getter")


async def Pushing(kst, state, repo) -> None:
    if not hk.api:
        return await kst.eod("Please set `HEROKU_API` in Config Vars.")
    if not hk.name:
        return await kst.eod("Please set `HEROKU_APP_NAME` in Config Vars.")
    try:
        conn = hk.heroku()
        app = conn.app(hk.name)
    except Exception as err:
        if str(err).lower().startswith("401 client error: unauthorized"):
            msg = "HEROKU_API invalid or expired... Please re-check."
        else:
            msg = err
        up = rf"""\\**#Getter**// **Heroku Error:**
`{msg}`"""
        return await kst.eor(up)
    await force_pull()
    up = rf"""\\**#Getter**// `{state}Updated Successfully...`
Wait for a few minutes, then run `{hl}ping` command."""
    yy = await kst.eor(up)
    try:
        chat_id = yy.chat_id or yy.from_id
        await sgvar("_restart", f"{chat_id}|{yy.id}")
    except BaseException:
        pass
    url = app.git_url.replace("https://", f"https://api:{hk.api}@")
    if "heroku" in repo.remotes:
        remote = repo.remote("heroku")
        remote.set_url(url)
    else:
        remote = repo.create_remote("heroku", url)
    try:
        remote.push(refspec="HEAD:refs/heads/main", force=True)
    except BaseException:
        pass
    build = app.builds(order_by="created_at", sort="desc")[0]
    if build.status != "succeeded":
        up = rf"""\\**#Getter**// `{state}Update Failed...`
Try again later or view logs for more info."""
        await kst.eod(up)


plugins_help["updater"] = {
    "{i}update": "Checks for updates, also displaying the changelog.",
    "{i}update [now/pull]": "Temporarily update as locally.",
    "{i}update [deploy/push]": "Permanently update as heroku.",
    "{i}update force": "Force temporarily update as locally.",
    "{i}repo": "Get repo link.",
    "{i}test": "Check the details.",
}
