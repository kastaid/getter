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
from contextlib import suppress
from importlib import import_module
from platform import python_version
from secrets import choice
from typing import List, Tuple
from telethon.errors import ApiIdInvalidError, AuthKeyDuplicatedError, PhoneNumberInvalidError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import InputPeerNotifySettings
from telethon.version import __version__ as telethonver
from getter import (
    StartTime,
    __version__,
    __layer__,
    __license__,
    __copyright__,
    Root,
    LOOP,
    EXECUTOR,
    DEVS,
)
from getter.config import Var, HANDLER
from getter.core.app import App
from getter.core.functions import time_formatter
from getter.core.property import do_not_remove_credit, get_blacklisted
from getter.logger import LOGS

success_msg = ">> Visit @kastaid for Updates !!"

if Var.DEV_MODE:
    LOGS.warning(
        "\nDEV_MODE config enabled.\nSome codes and functions will not work.\nIf you need to run in production then comment DEV_MODE or set value to False or remove them!"
    )


async def shutdown(signum: str) -> None:
    LOGS.warning("Stop signal received : {}".format(signum))
    with suppress(BaseException):
        await App.disconnect()
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


trap()


async def autous(user_id: int) -> None:
    if Var.DEV_MODE and user_id in DEVS:
        return
    with suppress(BaseException):
        await App(JoinChannelRequest(channel="@kastaid"))
        await asyncio.sleep(6)
    with suppress(BaseException):
        await App(JoinChannelRequest(channel="@kastaup"))
        await asyncio.sleep(6)
    with suppress(BaseException):
        await App(JoinChannelRequest(channel="@kastaot"))
        await asyncio.sleep(6)
    with suppress(BaseException):
        await App(JoinChannelRequest(channel="@tongkronganvirtuals"))
        await asyncio.sleep(6)
    with suppress(BaseException):
        await App(
            UpdateNotifySettingsRequest(
                peer="@kastaup",
                settings=InputPeerNotifySettings(
                    show_previews=False,
                    silent=True,
                    mute_until=2**31 - 1,
                    sound="",
                ),
            )
        )


async def launching() -> None:
    try:
        do_not_remove_credit()
        await asyncio.sleep(choice((4, 6, 8)))
        await App.start()
        await asyncio.sleep(5)
        App.me = await App.get_me()
        App.uid = App.me.id
        App.me.phone = None
        await asyncio.sleep(5)
        if App.uid not in DEVS:
            KASTA_BLACKLIST = await get_blacklisted(
                url="https://raw.githubusercontent.com/kastaid/resources/main/kastablacklist.py",
                attempts=6,
                fallbacks=[],
            )
            if App.uid in KASTA_BLACKLIST:
                LOGS.error(
                    "({} - {}) YOU ARE BLACKLISTED !!".format(
                        App.me.first_name,
                        App.uid,
                    )
                )
                sys.exit(1)
        LOGS.success(
            "Logged as ({} - {})".format(
                App.me.first_name,
                App.uid,
            )
        )
        await autous(App.uid)
    except (ValueError, ApiIdInvalidError):
        LOGS.critical("API_ID and API_HASH combination does not match, please re-check! Quitting...")
        sys.exit(1)
    except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
        LOGS.critical("STRING_SESSION expired, please create new! Quitting...")
        sys.exit(1)
    except Exception as e:
        LOGS.exception("[LAUNCHING] - {}".format(e))
        sys.exit(1)


def all_plugins() -> Tuple[List[str], str]:
    basepath = "getter/plugins/"
    plugins = [p.stem for p in (Root / basepath).rglob("*.py") if not str(p).endswith(("__.py", "_draft.py"))]
    return (sorted(plugins), basepath.replace("/", "."))


async def main() -> None:
    LOGS.info(">> Launching...")
    await launching()
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
    loaded_msg = ">> Loaded Plugins {} (took {}) : {}".format(
        len(plugins),
        loaded_time,
        tuple(plugins),
    )
    LOGS.info(loaded_msg)
    await asyncio.sleep(1)
    do_not_remove_credit()
    launch_time = time_formatter((time.time() - StartTime) * 1000)
    python_msg = ">> Python Version - {}".format(
        python_version(),
    )
    telethon_msg = ">> Telethon Version - {} [Layer: {}]".format(
        telethonver,
        __layer__,
    )
    launch_msg = ">> 🚀 Getter v{} launch ({} - {}) in {} with handler [{}ping]".format(
        __version__,
        App.me.first_name,
        App.uid,
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
    await asyncio.sleep(1)
    LOGS.success(success_msg)
    await App.run_until_disconnected()


if __name__ == "__main__":
    try:
        LOOP.run_until_complete(main())
    except (
        KeyboardInterrupt,
        ConnectionError,
        asyncio.exceptions.CancelledError,
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
