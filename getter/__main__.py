# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import sys
from importlib import import_module
from time import time
from requests.packages import urllib3
from . import (
    __license__,
    __copyright__,
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
)
from .config import Var, hl
from .core.base_client import getter_app
from .core.helper import plugins_help
from .core.patched import apply
from .core.property import do_not_remove_credit
from .core.startup import (
    trap,
    migrations,
    autopilot,
    verify,
    autous,
    finishing,
)
from .core.utils import time_formatter
from .logger import LOGS

apply()

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
    migrations()
    await autopilot()
    await verify()
    LOGS.info(">> Load Plugins...")
    load = time()
    plugins = getter_app.all_plugins
    for p in plugins:
        try:
            if p["path"].startswith("custom"):
                plugin = "getter.plugins." + p["path"]
            else:
                plugin = "getter." + p["path"]
            import_module(plugin)
            LOGS.success("[+] " + p["name"])
        except Exception as err:
            LOGS.exception(f"[-] {p['name']} : {err}")
    loaded_time = time_formatter((time() - load) * 1000)
    loaded_msg = ">> Loaded Plugins: {} , Commands: {} (took {}) : {}".format(
        plugins_help.count,
        plugins_help.total,
        loaded_time,
        tuple(_["name"] for _ in plugins),
    )
    LOGS.info(loaded_msg)
    do_not_remove_credit()
    python_msg = ">> Python Version - {}".format(
        __pyversion__,
    )
    telethon_msg = ">> Telethon Version - {} [Layer: {}]".format(
        __tlversion__,
        __layer__,
    )
    launch_msg = ">> 🚀 Getter v{} launch ({} - {}) in {} with handler [ {}ping ]".format(
        __version__,
        getter_app.full_name,
        getter_app.uid,
        getter_app.uptime,
        hl,
    )
    LOGS.info(python_msg)
    LOGS.info(telethon_msg)
    LOGS.info(launch_msg)
    LOGS.info(__license__)
    LOGS.info(__copyright__)
    await autous(getter_app.uid)
    await finishing(launch_msg)
    LOGS.success(success_msg)


if __name__ == "__main__":
    try:
        getter_app.run_in_loop(main())
        getter_app.run()
    except (
        KeyboardInterrupt,
        SystemExit,
        ConnectionError,
        asyncio.exceptions.CancelledError,
    ):
        pass
    except Exception as err:
        LOGS.exception(f"[MAIN_ERROR] : {err}")
    finally:
        LOGS.warning("[MAIN] - Getter Stopped...")
        sys.exit(0)
