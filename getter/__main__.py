# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import sys
from importlib import import_module
from time import monotonic
from requests.packages import urllib3
import getter.core.patched  # noqa
from getter import (
    __license__,
    __copyright__,
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
)
from getter.config import Var, hl
from getter.core.base_client import getter_app
from getter.core.helper import plugins_help
from getter.core.property import do_not_remove_credit
from getter.core.startup import (
    trap,
    migrations,
    autopilot,
    verify,
    autous,
    finishing,
)
from getter.core.utils import time_formatter
from getter.logger import LOG

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
    LOG.info(">> Load Plugins...")
    load = monotonic()
    plugins = getter_app.all_plugins
    for p in plugins:
        try:
            if p["path"].startswith("custom"):
                plugin = "getter.plugins." + p["path"]
            else:
                plugin = "getter." + p["path"]
            import_module(plugin)
            LOG.success("[+] " + p["name"])
        except Exception as err:
            LOG.exception(f"[-] {p['name']} : {err}")
    loaded_time = time_formatter((monotonic() - load) * 1000)
    loaded_msg = ">> Loaded Plugins: {} , Commands: {} (took {}) : {}".format(
        plugins_help.count,
        plugins_help.total,
        loaded_time,
        tuple(_["name"] for _ in plugins),
    )
    LOG.info(loaded_msg)
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
    except (
        KeyboardInterrupt,
        SystemExit,
    ):
        pass
    except Exception as err:
        LOG.exception(f"[MAIN_ERROR] : {err}")
    finally:
        LOG.warning("[MAIN] - Getter Stopped...")
        sys.exit(0)
