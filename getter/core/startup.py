# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import signal
from contextlib import suppress
from typing import List, Tuple
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.types import InputPeerNotifySettings
from .. import (
    Root,
    LOOP,
    EXECUTOR,
    DEVS,
)
from ..config import Var
from ..logger import LOGS
from .client import getter_app
from .helper import Hk
from .property import (
    _c,
    _u,
    _g,
    _v,
)


async def shutdown(signum: str) -> None:
    LOGS.warning("Stop signal received : {}".format(signum))
    with suppress(BaseException):
        await getter_app.disconnect()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    EXECUTOR.shutdown(wait=False)
    await LOOP.shutdown_asyncgens()
    LOOP.stop()


def trap() -> None:
    for signame in ("SIGINT", "SIGTERM", "SIGABRT"):
        sig = getattr(signal, signame)
        LOOP.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s.name)))


def migrations(app=None) -> None:
    if Var.DEV_MODE or not Hk.is_heroku:
        return
    try:
        if not app:
            app = Hk.heroku().app(Hk.name)
    except Exception as err:
        LOGS.exception("[MIGRATIONS] - {}".format(err))
        return
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
        if not [a for a in addons if str(a.plan.name).lower().startswith(pg)]:
            app.install_addon(pg, config={"version": pgv})
    else:
        app.install_addon(pg, config={"version": pgv})
    if Hk.stack != "container":
        app.update_buildpacks(
            [
                "https://github.com/heroku/heroku-buildpack-python",
                "https://github.com/heroku/heroku-buildpack-apt",
                "https://github.com/heroku/heroku-buildpack-google-chrome",
                "https://github.com/heroku/heroku-buildpack-chromedriver",
                "https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest",
            ]
        )


async def autous(user_id: int) -> None:
    if Var.DEV_MODE and user_id in DEVS:
        return
    with suppress(BaseException):
        await getter_app.join_chat(_c)
        await asyncio.sleep(6)
    with suppress(BaseException):
        await getter_app.join_chat(_u)
        await asyncio.sleep(6)
    with suppress(BaseException):
        await getter_app.join_chat(_g)
        await asyncio.sleep(6)
    with suppress(BaseException):
        await getter_app.join_chat(_v)
        await asyncio.sleep(6)
    with suppress(BaseException):
        await getter_app(
            UpdateNotifySettingsRequest(
                peer=_u,
                settings=InputPeerNotifySettings(
                    show_previews=False,
                    silent=True,
                    mute_until=2**31 - 1,
                    sound="",
                ),
            )
        )


def all_plugins() -> Tuple[List[str], str]:
    basepath = "getter/plugins/"
    plugins = [p.stem for p in (Root / basepath).rglob("*.py") if not str(p).endswith(("__.py", "_draft.py"))]
    return (sorted(plugins), basepath.replace("/", "."))
