# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import sys
from importlib import import_module
from time import monotonic

from requests.packages import urllib3

import getter.core.patched  # noqa

from . import (
    __copyright__,
    __layer__,
    __license__,
    __pyversion__,
    __tlversion__,
    __version__,
)
from .config import Var, hl
from .core.base_client import getter_app
from .core.db import db_connect
from .core.helper import jdata, plugins_help
from .core.property import do_not_remove_credit
from .core.startup import (
    autopilot,
    autous,
    finishing,
    migrations,
    trap,
    verify,
)
from .core.utils import time_formatter
from .logger import LOG

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

success_msg = ">> Visit @kastaid for Updates !!"
if Var.DEV_MODE:
    trap()
    print(
        "\nDEV_MODE config enabled.\n"
        + "Some codes and functionality will not work normally.\n"
        + "If you need to run in Production then comment DEV_MODE or set value to False or remove them!\n"
    )


async def main() -> None:
    await db_connect()
    await jdata.sudo_users()
    migrations()
    await autopilot()
    await verify()
    await getter_app.start_pytgcalls()
    LOG.info(">> Load Plugins...")
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
    loaded_time = time_formatter((monotonic() - load) * 1000)
    loaded_msg = ">> Loaded Plugins: {} , Commands: {} (took {}) : {}".format(
        plugins_help.count,
        plugins_help.total,
        loaded_time,
        tuple(_["name"] for _ in plugins),
    )
    LOG.info(loaded_msg)
    do_not_remove_credit()
    python_msg = f">> Python Version - {__pyversion__}"
    telethon_msg = f">> Telethon Version - {__tlversion__} [Layer: {__layer__}]"
    launch_msg = f">> 🚀 Getter v{__version__} launch ({getter_app.full_name} - {getter_app.uid}) in {getter_app.uptime} with handler [ {hl}ping ]"
    LOG.info(python_msg)
    LOG.info(telethon_msg)
    LOG.info(launch_msg)
    LOG.info(__license__)
    LOG.info(__copyright__)
    await autous(getter_app.uid)
    await finishing(launch_msg)
    LOG.success(success_msg)


if __name__ == "__main__":
    try:
        getter_app.run_in_loop(main())
        getter_app.run()
    except (KeyboardInterrupt, SystemExit):
        LOG.warning("[MAIN] - Manual stop signal received.")
        sys.exit(0)
    except Exception as err:
        LOG.exception(f"[MAIN_ERROR]: {err}")
        sys.exit(1)
    finally:
        LOG.warning("[MAIN] - Stopped...")
