# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import sys
from asyncio import Lock, sleep
from contextlib import suppress
from os import close, execl, getpid
from secrets import choice
import psutil as psu
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from heroku3 import from_key
from . import (
    __version__,
    Root,
    HELP,
    DEVS,
    Var,
    hl,
    kasta_cmd,
    Runner,
)

UPDATE_LOCK = Lock()
UPSTREAM_REPO = "https://github.com/kastaid/getter.git"
UPSTREAM_BRANCH = "main"
help_text = f"""❯ `{hl}update <now|pull|one> <force|f>`
Temporary update as locally if available from repo.

❯ `{hl}update <deploy|push|all>`
Permanently update as heroku, will forced deploy.
"""


async def ignores() -> None:
    rems = ".github docs README.md LICENSE scripts run.py requirements-dev.txt setup.cfg .editorconfig .deepsource.toml session.py"
    return await Runner(f"rm -rf -- {rems}")


def verify(repo, diff) -> bool:
    v = ""
    for c in repo.iter_commits(diff):
        v = str(c.count())
    return bool(v)


def generate_changelog(repo, diff) -> str:
    chlog = ""
    rep = UPSTREAM_REPO.replace(".git", "")
    ch = f"<b>Getter v{__version__} updates for <a href={rep}/tree/{UPSTREAM_BRANCH}>[{UPSTREAM_BRANCH}]</a>:</b>"
    date = "%d/%m/%Y %H:%M:%S"
    for c in repo.iter_commits(diff):
        chlog += f"\n\n<b>#{c.count()}</b> [<code>{c.committed_datetime.strftime(date)}</code>]\n<code>{c.hexsha}</code>\n<b><a href={rep.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> ~ <code>{c.author}</code>"
    if chlog:
        return str(ch + chlog)
    return chlog


async def show_changelog(e, changelog):
    file = "changelog_output.txt"
    if len(changelog) > 4096:
        await e.eor("View the file to see it.")
        with open(file, "w+") as f:
            f.write(changelog)
        await e.reply(file=file, silent=True)
        (Root / file).unlink(missing_ok=True)
    else:
        await e.eor(changelog, parse_mode="html")


async def pulling(e):
    await Runner(f"git pull -f && git reset --hard origin/{UPSTREAM_BRANCH}")
    await ignores()
    await Runner("pip3 install --no-cache-dir -U -r requirements.txt")
    await e.eor(f"`[PULL] Updated Successfully...`\nWait for a few seconds, then run `{hl}ping` command.")
    with suppress(psu.NoSuchProcess, psu.AccessDenied, psu.ZombieProcess):
        c_p = psu.Process(getpid())
        [close(h.fd) for h in c_p.open_files() + c_p.connections()]
    execl(sys.executable, sys.executable, "-m", "getter")
    return


async def pushing(e):
    if not Var.HEROKU_API:
        await e.eod("Please set `HEROKU_API` in Config Vars.")
        return
    if not Var.HEROKU_APP_NAME:
        await e.eod("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        heroku_conn = from_key(Var.HEROKU_API)
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
    except Exception as err:
        await e.eod(f"**ERROR**\n`{err}`")
        return
    """
    # migration new vars
    cfg = app.config()
    if "HEROKU_API_KEY" in cfg:
        cfg["HEROKU_API"] = cfg["HEROKU_API_KEY"]
        del cfg["HEROKU_API_KEY"]
    """
    await Runner(f"git pull -f && git reset --hard origin/{UPSTREAM_BRANCH}")
    await ignores()
    await e.eor(f"`[PUSH] Updated Successfully...`\nWait for a few minutes, then run `{hl}ping` command.")
    push = f"git push -f https://heroku:{Var.HEROKU_API}@git.heroku.com/{Var.HEROKU_APP_NAME}.git HEAD:main"
    _, err = await Runner(push)
    if err:
        await e.eor(f"`[PUSH] Deploy Failed: {err}`\nTry again later or view logs for more info.")
    build = app.builds(order_by="created_at", sort="desc")[0]
    if build.status == "failed":
        await e.eor("`[PUSH] Build Failed...`\nTry again later or view logs for more info.")
    return


@kasta_cmd(pattern="update(?: |$)(now|deploy|pull|push|one|all)?(?: |$)(.*)")
@kasta_cmd(own=True, senders=DEVS, pattern="getterup(?: |$)(now|deploy|pull|push|one|all)?(?: |$)(.*)")
async def _(e):
    is_devs = True if not (hasattr(e, "out") and e.out) else False
    if UPDATE_LOCK.locked():
        await e.eor("`Please wait until previous UPDATE finished...`", time=5, silent=True)
        return
    async with UPDATE_LOCK:
        mode = e.pattern_match.group(1)
        opt = e.pattern_match.group(2)
        is_deploy = is_now = force_now = False
        if mode in ["deploy", "push", "all"]:
            is_deploy = True
        if mode in ["now", "pull", "one"]:
            is_now = True
        if not Var.DEV_MODE and is_now and opt in ["force", "f"]:
            force_now = True
        if is_devs and opt and not force_now:
            user_id = version = None
            try:
                user_id = int(opt)
            except ValueError:
                version = opt
            if not version and user_id != e.client.uid:
                return
            if not user_id and version == __version__:
                return
        if is_devs:
            await sleep(choice((4, 6, 8)))
        Kst = await e.eor("`Fetching...`", silent=True)
        try:
            repo = Repo()
        except NoSuchPathError as err:
            await Kst.eor(f"`Directory not found : {err}`")
            return
        except GitCommandError as err:
            await Kst.eor(f"`Early failure : {err}`")
            return
        except InvalidGitRepositoryError:
            repo = Repo.init()
            origin = repo.create_remote("origin", UPSTREAM_REPO)
            origin.fetch()
            repo.create_head("main", origin.refs.main)
            repo.heads.main.set_tracking_branch(origin.refs.main)
            repo.heads.main.checkout(True)
        await Runner(f"git fetch origin {UPSTREAM_BRANCH}")
        if is_deploy:
            if is_devs:
                await sleep(choice((2, 3, 4)))
            await Kst.eor("`[PUSH] Updating ~ Please Wait...`")
            await pushing(Kst)
            return
        try:
            verif = verify(repo, f"HEAD..origin/{UPSTREAM_BRANCH}")
        except BaseException:
            verif = None
        if not (verif or force_now):
            await Kst.eor(f"`Getter v{__version__} up-to-date as {UPSTREAM_BRANCH}`", time=15)
            return
        if not (mode or force_now):
            changelog = generate_changelog(repo, f"HEAD..origin/{UPSTREAM_BRANCH}")
            await show_changelog(Kst, changelog)
            await Kst.reply(help_text, silent=True)
            return
        if force_now:
            await Kst.eor("`[PULL] Force-Syncing to latest source code...`")
            await sleep(2)
        if is_now:
            await Kst.eor("`[PULL] Updating ~ Please Wait...`")
            await pulling(Kst)
        return


@kasta_cmd(pattern="repo$")
async def _(e):
    await e.eor(
        """
• **Repo:** [GitHub](https://kasta.vercel.app/repo?c=getter)
• **Deploy:** [View at @kastaid](https://kasta.vercel.app/getter_deploy)
""",
    )


HELP.update(
    {
        "updater": [
            "Updater",
            """❯ `{i}update`
Checks for updates, also displaying the changelog.

❯ `{i}update <now|pull|one> <force|f>`
Temporary update as locally if available from repo.

❯ `{i}update <deploy|push|all>`
Permanently update as heroku, will forced deploy.

❯ `{i}repo`
Get repo link.
""",
        ]
    }
)
