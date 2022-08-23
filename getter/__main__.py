# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import signal
import sys
import time
from importlib import import_module
from requests.packages import urllib3
from . import (
    StartTime,
    __license__,
    __copyright__,
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
    LOOP,
)
from .config import Var, HANDLER
from .core.client import getter_app
from .core.functions import time_formatter
from .core.helper import plugins_help
from .core.property import do_not_remove_credit
from .core.startup import (
    shutdown,
    migrations,
    all_plugins,
    autous,
)
from .logger import LOGS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

success_msg = ">> Visit @kastaid for Updates !!"

if Var.DEV_MODE:
    LOGS.warning(
        "\nDEV_MODE config enabled.\nSome codes and functions will not work.\nIf you need to run in production then comment DEV_MODE or set value to False or remove them!"
    )


def trap() -> None:
    for signame in ("SIGINT", "SIGTERM", "SIGABRT"):
        sig = getattr(signal, signame)
        LOOP.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s.name)))


trap()


async def main() -> None:
    LOGS.info(">> Migrations...")
    migrations()
    LOGS.info(">> Load Plugins...")
    load = time.time()
    plugins, basepath = all_plugins()
    for plugin in plugins:
        try:
            import_module(basepath + plugin)
            LOGS.success("[+] " + plugin)
        except Exception as err:
            LOGS.exception("[-] {} : {}".format(plugin, err))
    loaded_time = time_formatter((time.time() - load) * 1000)
    loaded_msg = ">> Loaded Plugins: {} , Commands: {} (took {}) : {}".format(
        len(plugins),
        sum(len(v) for v in plugins_help.values()),
        loaded_time,
        tuple(plugins),
    )
    LOGS.info(loaded_msg)
    await asyncio.sleep(1)
    do_not_remove_credit()
    launch_time = time_formatter((time.time() - StartTime) * 1000)
    python_msg = ">> Python Version - {}".format(
        __pyversion__,
    )
    telethon_msg = ">> Telethon Version - {} [Layer: {}]".format(
        __tlversion__,
        __layer__,
    )
    launch_msg = ">> 🚀 Getter v{} launch ({} - {}) in {} with handler [{}ping]".format(
        __version__,
        getter_app.full_name,
        getter_app.uid,
        launch_time,
        HANDLER,
    )
    LOGS.info(python_msg)
    LOGS.info(telethon_msg)
    LOGS.info(launch_msg)
    await asyncio.sleep(1)
    LOGS.info(__license__)
    await asyncio.sleep(1)
    LOGS.info(__copyright__)
    await autous(getter_app.uid)
    LOGS.success(success_msg)
    await getter_app.run()


if __name__ == "__main__":
    try:
        LOOP.run_until_complete(main())
    except (
        KeyboardInterrupt,
        ConnectionError,
        asyncio.CancelledError,
    ):
        pass
    except (ModuleNotFoundError, ImportError) as err:
        LOGS.exception("[MAIN_MODULE_IMPORT] : {}".format(err))
        sys.exit(1)
    except Exception as err:
        LOGS.exception("[MAIN_ERROR] : {}".format(err))
    finally:
        LOGS.warning("[MAIN] - App Stopped...")
        sys.exit(0)
