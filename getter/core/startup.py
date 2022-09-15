# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import signal
import typing
from contextlib import suppress
from datetime import timedelta
from async_timeout import timeout as WaitFor
from telethon.tl import functions as fun, types as typ
from .. import __version__, Root
from ..config import Var, EXECUTOR, DEVS
from ..logger import LOGS
from .client import getter_app
from .db.globals_db import gvar, sgvar, dgvar
from .helper import hk, get_botlogs
from .property import (
    _c,
    _u,
    _g,
    _v,
)
from .utils import humanbool

_about = """GETTER BOTLOGS

Chat ID: {}
Your ID: {}

⚠️  DO NOT DELETE THIS GROUP  ⚠️

Our Channel: @kastaid
"""
_warn = """<b>⚠️ DO NOT LEAVE OR,
⚠️ DO NOT DELETE OR,
⚠️ DO NOT CHANGE THE SETTINGS OF THIS GROUP!</b>


<b><u>IF IGNORED THIS MESSAGE THE BOT WILL NOT WORK</u></b>


<b>Chat ID:</b> <code>{}</code>
<b>Your ID:</b> <code>{}</code>

<b>Our Channel:</b> @kastaid
"""
_restart_text = r"""
\\**#Getter**// **is back and alive!**
├  **Sudo:** `{}`
├  **PM-Guard:** `{}`
├  **PM-Block:** `{}`
├  **Anti-PM:** `{}`
└  **Version:** `{}`
"""
_reboot_text = r"""
\\**#Getter**// **is rebooted and applied!**
├  **Sudo:** `{}`
├  **PM-Guard:** `{}`
├  **PM-Block:** `{}`
├  **Anti-PM:** `{}`
└  **Version:** `{}`
"""


async def shutdown(signum: str) -> None:
    LOGS.warning(f"Stop signal received : {signum}")
    loop = asyncio.get_event_loop()
    with suppress(BaseException):
        await getter_app.disconnect()
    tasks = [_ for _ in asyncio.all_tasks() if _ is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    EXECUTOR.shutdown(wait=False)
    await loop.shutdown_asyncgens()
    loop.stop()


def trap() -> None:
    for signame in ("SIGINT", "SIGTERM", "SIGABRT"):
        sig = getattr(signal, signame)
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s.name)))


def migrations(app=None) -> None:
    if Var.DEV_MODE or not hk.is_heroku:
        return
    LOGS.info(">> Migrations...")
    try:
        if not app:
            app = hk.heroku().app(hk.name)
    except Exception as err:
        LOGS.exception(err)
        return
    LOGS.warning(
        "Heroku free tier discountinued as of 11/28/2022, read more details at https://blog.heroku.com/next-chapter"
    )
    """
    # migration new vars
    cfg = app.config()
    if "HEROKU_API_KEY" in cfg:
        cfg["HEROKU_API"] = cfg["HEROKU_API_KEY"]
        del cfg["HEROKU_API_KEY"]
    """
    addons = app.addons()
    pg, pgv = "heroku-postgresql", "14"
    if addons:
        if not [_ for _ in addons if str(_.plan.name).lower().startswith(pg)]:
            app.install_addon(pg, config={"version": pgv})
    else:
        app.install_addon(pg, config={"version": pgv})
    if hk.stack != "container":
        app.update_buildpacks(
            [
                "https://github.com/heroku/heroku-buildpack-python",
                "https://github.com/heroku/heroku-buildpack-apt",
                "https://github.com/heroku/heroku-buildpack-google-chrome",
                "https://github.com/heroku/heroku-buildpack-chromedriver",
                "https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest",
            ]
        )


async def autopilot() -> None:
    if Var.BOTLOGS or gvar("BOTLOGS"):
        return
    LOGS.info(">> Auto-Pilot...")
    photo = None
    with suppress(BaseException):
        photo = await getter_app.upload_file("assets/getter_botlogs.png")
        await asyncio.sleep(2)
    LOGS.info("Creating a group for BOTLOGS...")
    _, chat_id = await getter_app.create_group(
        title="GETTER BOTLOGS",
        about="",
        users=["@MissRose_bot"],
        photo=photo,
    )
    if not chat_id:
        LOGS.warning("Something happened while creating a group for BOTLOGS, please report this one to our developers!")
        return
    sgvar("BOTLOGS", chat_id)
    with suppress(BaseException):
        await asyncio.sleep(2)
        await getter_app(
            fun.messages.EditChatAboutRequest(
                chat_id,
                about=_about.format(chat_id, getter_app.uid),
            )
        )
    with suppress(BaseException):
        msg = await getter_app.send_message(chat_id, _warn.format(chat_id, getter_app.uid), parse_mode="html")
        await asyncio.sleep(2)
        await msg.pin(notify=True)
    LOGS.success("Successfully to created a group for BOTLOGS.")
    await asyncio.sleep(1)
    print(f"\nBOTLOGS = {chat_id}\n")
    await asyncio.sleep(1)
    LOGS.info("Save the BOTLOGS ID above, might be useful for the future :)")


async def verify() -> None:
    BOTLOGS = get_botlogs()
    if not BOTLOGS:
        return
    ls = None
    with suppress(BaseException):
        ls = await getter_app.get_entity(BOTLOGS)
    if not ls:
        return
    if not (isinstance(ls, typ.User) and ls.creator) and ls.default_banned_rights.send_messages:
        LOGS.critical(
            "Your account doesn't have permission to send messages in the BOTLOGS group. Please re-check that ID is correct or change the group permissions to send messages and send media!"
        )


async def autous(user_id: int) -> None:
    if Var.DEV_MODE and user_id in DEVS:
        return
    await getter_app.join_to(_c)
    await asyncio.sleep(6)
    await getter_app.join_to(_u)
    await asyncio.sleep(6)
    await getter_app.join_to(_g)
    await asyncio.sleep(6)
    await getter_app.join_to(_v)
    await asyncio.sleep(6)
    await getter_app.mute_chat(_u)


async def finishing(launch_msg: str) -> None:
    BOTLOGS = get_botlogs()
    is_restart, is_reboot = False, False
    with suppress(BaseException):
        _restart = gvar("_restart").split("|")
        is_restart = bool(_restart)
    with suppress(BaseException):
        _reboot = gvar("_reboot").split("|")
        is_reboot = bool(_reboot)
    if is_restart:
        with suppress(BaseException):
            chat_id, msg_id = int(_restart[0]), int(_restart[1])
            async with WaitFor(5):
                await getter_app.edit_message(
                    chat_id,
                    message=msg_id,
                    text=_restart_text.format(
                        humanbool(gvar("_sudo"), toggle=True),
                        humanbool(gvar("_pmguard"), toggle=True),
                        humanbool(gvar("_pmblock"), toggle=True),
                        humanbool(gvar("_antipm"), toggle=True),
                        __version__,
                    ),
                    link_preview=False,
                )
        dgvar("_restart")
    if is_reboot:
        with suppress(BaseException):
            chat_id, msg_id = int(_reboot[0]), int(_reboot[1])
            await getter_app.edit_message(
                chat_id,
                message=msg_id,
                text=_reboot_text.format(
                    humanbool(gvar("_sudo"), toggle=True),
                    humanbool(gvar("_pmguard"), toggle=True),
                    humanbool(gvar("_pmblock"), toggle=True),
                    humanbool(gvar("_antipm"), toggle=True),
                    __version__,
                ),
                link_preview=False,
            )
        dgvar("_reboot")
    if BOTLOGS:
        with suppress(BaseException):
            text = f"<pre>{launch_msg}</pre>"
            text += "\n(c) @kastaid #getter #launch"
            await getter_app.send_message(
                BOTLOGS,
                text,
                parse_mode="html",
                schedule=timedelta(seconds=10),
            )


def all_plugins() -> typing.Tuple[typing.List[str], str]:
    basepath = "getter/plugins/"
    plugins = [_.stem for _ in (Root / basepath).rglob("*.py") if not str(_).endswith(("__.py", "_draft.py"))]
    return sorted(plugins), basepath.replace("/", ".")
