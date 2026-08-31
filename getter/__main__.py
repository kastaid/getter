# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import sys
from importlib import import_module
from time import monotonic

import uvloop

import getter.core.patched  # noqa

from . import (
    __copyright__,
    __layer__,
    __license__,
    __pyversion__,
    __tlversion__,
    __version__,
)
from .config import Var
from .core.db import (
    database_connect,
    database_disconnect,
)
from .core.helper import jdata, plugins_help
from .core.kasta import getter_app
from .core.property import do_not_remove_credit
from .core.startup import (
    autopilot,
    autous,
    finishing,
    migrations,
    verify,
)
from .core.utils import format_time
from .logger import LOG

success_msg = "> Visit @kastaid for Updates !!"
if Var.DEV_MODE:
    print(
        "\nDEV_MODE config enabled.\n"
        + "Some codes and functionality will not work normally.\n"
        + "If you need to run in Production then comment DEV_MODE or set value to False or remove them!\n"
    )


async def main() -> None:
    await database_connect()
    await jdata.sudo_users()
    migrations()
    await autopilot()
    await verify()
    LOG.info("> Load Plugins...")
    load = monotonic()
    plugins = getter_app.all_plugins
    for p in plugins:
        try:
            plugin = (
                "".join(("getter.plugins.", p["path"]))
                if p["path"].startswith("custom")
                else "".join(("getter.", p["path"]))
            )
            import_module(plugin)
            LOG.success("[+] " + p["name"])
        except Exception as err:
            LOG.exception(f"[-] {p['name']}: {err}")
    from .plugins.afk import handle_afk
    from .plugins.pmpermit import handle_pmpermit

    await asyncio.gather(*[handle_afk(), handle_pmpermit()])
    loaded_time = format_time(monotonic() - load)
    loaded_msg = "> Loaded Plugins: {} , Commands: {} (took {}) : {}".format(
        plugins_help.count,
        plugins_help.total,
        loaded_time,
        tuple(_["name"] for _ in plugins),
    )
    LOG.info(loaded_msg)
    do_not_remove_credit()
    python_msg = f"> Python Version - {__pyversion__}"
    telethon_msg = f"> Telethon Version - {__tlversion__} [Layer: {__layer__}]"
    launch_msg = f"> 🚀 Getter v{__version__} launch ({getter_app.full_name} - {getter_app.uid}) in {getter_app.uptime} with handler [ {Var.PREFIX}ping ]"
    LOG.info(python_msg)
    LOG.info(telethon_msg)
    LOG.info(launch_msg)
    LOG.info(__license__)
    LOG.info(__copyright__)
    await autous(getter_app.uid)
    await finishing(launch_msg)
    LOG.success(success_msg)


async def run() -> None:
    try:
        await getter_app.start_client()
        await main()
        await getter_app.run_until_disconnected()
    finally:
        await database_disconnect()
        if getter_app.is_connected():
            await getter_app.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(
            run(),
            loop_factory=uvloop.new_event_loop,
        )
    except KeyboardInterrupt:
        LOG.info("[APP] shutdown signal received")
    except Exception:
        LOG.exception("[APP] unhandled exception")
        sys.exit(1)
    finally:
        LOG.info("[APP] stopped")
