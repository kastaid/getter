# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import signal
from typing import Any

from telethon.tl import functions as fun, types as typ

from getter import EXECUTOR, LOOP, __version__
from getter.config import DEVS, Var
from getter.logger import LOG

from .base_client import getter_app
from .db import (
    db_disconnect,
    dgvar,
    gvar,
    sgvar,
)
from .helper import get_botlogs, hk
from .property import _c, _g, _u
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
├  **PM-Logs:** `{}`
├  **PM-Block:** `{}`
├  **Anti-PM:** `{}`
└  **Version:** `{}`
"""
_reboot_text = r"""
\\**#Getter**// **is rebooted and applied!**
├  **Sudo:** `{}`
├  **PM-Guard:** `{}`
├  **PM-Logs:** `{}`
├  **PM-Block:** `{}`
├  **Anti-PM:** `{}`
└  **Version:** `{}`
"""


async def shutdown(signum: str) -> None:
    LOG.warning(f"Stop signal received : {signum}")
    try:
        await db_disconnect()
    except BaseException:
        pass
    try:
        await getter_app.disconnect()
    except BaseException:
        pass
    tasks = [i for i in asyncio.all_tasks() if i is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    EXECUTOR.shutdown(wait=False)
    await LOOP.shutdown_asyncgens()
    LOOP.stop()


def trap() -> None:
    for signame in ("SIGINT", "SIGTERM", "SIGABRT"):
        sig = getattr(signal, signame)
        LOOP.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s.name)))


def migrations(app: Any = None) -> None:
    if Var.DEV_MODE or not hk.is_heroku:
        return
    LOG.info(">> Migrations...")
    try:
        if not app:
            app = hk.heroku().app(hk.name)
    except Exception as err:
        LOG.exception(err)
        return
    LOG.warning(
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
        if not [i for i in addons if str(i.plan.name).lower().startswith(pg)]:
            app.install_addon(pg, config={"version": pgv})
    else:
        app.install_addon(pg, config={"version": pgv})
    if hk.stack != "container":
        app.update_buildpacks(
            [
                "https://github.com/heroku/heroku-buildpack-python",
                "https://github.com/heroku/heroku-buildpack-apt",
                "https://github.com/heroku/heroku-buildpack-chrome-for-testing",
                "https://github.com/heroku/heroku-buildpack-activestorage-preview",
            ]
        )


async def autopilot() -> None:
    if Var.BOTLOGS or await gvar("BOTLOGS"):
        return
    LOG.info(">> Auto-Pilot...")
    photo = None
    try:
        photo = await getter_app.upload_file("assets/getter.png")
        await asyncio.sleep(3)
    except BaseException:
        pass
    LOG.info("Creating a group for BOTLOGS...")
    _, chat_id = await getter_app.create_group(
        title="GETTER BOTLOGS",
        about="",
        users=["@MissRose_bot"],
        photo=photo,
    )
    if not chat_id:
        LOG.warning("Something happened while creating a group for BOTLOGS, please report this one to our developers!")
        return
    await sgvar("BOTLOGS", chat_id)
    try:
        await asyncio.sleep(3)
        await getter_app(
            fun.messages.EditChatAboutRequest(
                chat_id,
                about=_about.format(chat_id, getter_app.uid),
            )
        )
    except BaseException:
        pass
    try:
        msg = await getter_app.send_message(chat_id, _warn.format(chat_id, getter_app.uid), parse_mode="html")
        await asyncio.sleep(3)
        await msg.pin(notify=True)
    except BaseException:
        pass
    LOG.success("Successfully to created a group for BOTLOGS.")
    await asyncio.sleep(1)
    print(f"\nBOTLOGS = {chat_id}\n")
    await asyncio.sleep(1)
    LOG.info("Save the BOTLOGS ID above, might be useful for the future :)")


async def verify() -> None:
    BOTLOGS = await get_botlogs()
    if not BOTLOGS:
        return
    ls = None
    try:
        ls = await getter_app.get_entity(BOTLOGS)
    except BaseException:
        pass
    if not ls:
        return
    if not (isinstance(ls, typ.User) and ls.creator) and ls.default_banned_rights.send_messages:
        LOG.critical(
            "Your account doesn't have permission to send messages in the BOTLOGS group. Please re-check that ID is correct or change the group permissions to send messages and send media!"
        )


async def autous(user_id: int) -> None:
    if Var.DEV_MODE and user_id in DEVS:
        return
    await getter_app.join_to(_c)
    await asyncio.sleep(6)
    await getter_app.join_to(_u)
    await asyncio.sleep(6)
    await getter_app.mute_chat(_u)
    await asyncio.sleep(6)
    await getter_app.join_to(_g)


async def finishing(text: str) -> None:
    BOTLOGS = await get_botlogs()
    is_restart, is_reboot = False, False
    try:
        restart = (await gvar("_restart")).split("|")
        is_restart = True
    except BaseException:
        pass
    try:
        reboot = (await gvar("_reboot")).split("|")
        is_reboot = True
    except BaseException:
        pass
    if is_restart:
        try:
            chat_id, msg_id = int(restart[0]), int(restart[1])
            async with asyncio.timeout(5):
                await getter_app.edit_message(
                    chat_id,
                    message=msg_id,
                    text=_restart_text.format(
                        humanbool(await gvar("_sudo"), toggle=True),
                        humanbool(await gvar("_pmguard"), toggle=True),
                        humanbool(await gvar("_pmlog"), toggle=True),
                        humanbool(await gvar("_pmblock"), toggle=True),
                        humanbool(await gvar("_antipm"), toggle=True),
                        __version__,
                    ),
                    link_preview=False,
                )
            await asyncio.sleep(3)
        except BaseException:
            pass
        await dgvar("_restart")
    if is_reboot:
        try:
            chat_id, msg_id = int(reboot[0]), int(reboot[1])
            async with asyncio.timeout(5):
                await getter_app.edit_message(
                    chat_id,
                    message=msg_id,
                    text=_reboot_text.format(
                        humanbool(await gvar("_sudo"), toggle=True),
                        humanbool(await gvar("_pmguard"), toggle=True),
                        humanbool(await gvar("_pmlog"), toggle=True),
                        humanbool(await gvar("_pmblock"), toggle=True),
                        humanbool(await gvar("_antipm"), toggle=True),
                        __version__,
                    ),
                    link_preview=False,
                )
            await asyncio.sleep(3)
        except BaseException:
            pass
        await dgvar("_reboot")
    if BOTLOGS:
        try:
            text += "\n(c) @kastaid #getter #launch"
            await getter_app.send_message(
                BOTLOGS,
                text,
                parse_mode="html",
                link_preview=False,
                silent=True,
            )
        except BaseException:
            pass
