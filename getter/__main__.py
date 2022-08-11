# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import asyncio
import signal
import sys
from contextlib import suppress
from importlib import import_module
from secrets import choice
from time import time
from telethon.errors import ApiIdInvalidError, AuthKeyDuplicatedError, PhoneNumberInvalidError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import InputPeerNotifySettings
from getter import (
    StartTime,
    __version__,
    Root,
    LOOP,
)
from getter.app import App
from getter.config import Var
from getter.logger import LOGS
from getter.utils import time_formatter

success_msg = ">> Visit @kastaid for updates !!"

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
    LOGS.warning("Cancelling outstanding tasks : {}".format(len(tasks)))
    await asyncio.gather(*tasks, return_exceptions=True)
    await LOOP.shutdown_asyncgens()
    LOOP.stop()


def trap() -> None:
    for signame in {"SIGINT", "SIGTERM", "SIGABRT"}:
        sig = getattr(signal, signame)
        LOOP.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s.name)))


trap()


async def autous() -> None:
    if Var.DEV_MODE:
        return
    with suppress(BaseException):
        await asyncio.sleep(5)
        await App(JoinChannelRequest(channel="@kastaid"))
    with suppress(BaseException):
        await asyncio.sleep(5)
        await App(JoinChannelRequest(channel="@kastaot"))
    with suppress(BaseException):
        await asyncio.sleep(5)
        await App(JoinChannelRequest(channel="@kastaup"))
    with suppress(BaseException):
        await asyncio.sleep(5)
        await App(JoinChannelRequest(channel="@tongkronganvirtuals"))
    with suppress(BaseException):
        await asyncio.sleep(5)
        await App(
            UpdateNotifySettingsRequest(
                peer="@kastaup",
                settings=InputPeerNotifySettings(
                    show_previews=False,
                    silent=True,
                    mute_until=2 ** 31 - 1,
                    sound="",
                ),
            )
        )


async def launching() -> None:
    try:
        await asyncio.sleep(choice((2, 4, 6)))
        await App.start()
        await asyncio.sleep(5)
        App.me = await App.get_me()
        App.uid = App.me.id
        await autous()
    except ApiIdInvalidError:
        LOGS.error("API_ID and API_HASH combination does not match, please re-check! Quitting...")
        sys.exit(1)
    except (AuthKeyDuplicatedError, PhoneNumberInvalidError, EOFError):
        LOGS.error("STRING_SESSION expired, please create new! Quitting...")
        sys.exit(1)
    except Exception as e:
        LOGS.exception("[LAUNCHING] - {}".format(e))
        sys.exit(1)


def all_plugins():
    return sorted(
        [f.stem for f in (Root / "getter/plugins").rglob("*.py") if f.is_file() and not str(f).endswith("__init__.py")]
    )


async def main() -> None:
    LOGS.info(">> Launching...")
    await launching()
    LOGS.info(">> Load Plugins...")
    plugins = all_plugins()
    [import_module("getter.plugins." + p) for p in plugins]
    LOGS.info(">> Loaded Plugins {} : {}".format(len(plugins), str(plugins)))
    launch_time = time_formatter((time() - StartTime) * 1000)
    launch_msg = ">> 🚀 Getter v{} launch {} in {}".format(__version__, App.uid, launch_time)
    LOGS.info(launch_msg)
    await asyncio.sleep(2)
    LOGS.info(success_msg)
    await App.run_until_disconnected()


if __name__ == "__main__":
    try:
        LOOP.run_until_complete(main())
    except (
        NotImplementedError,
        KeyboardInterrupt,
        SystemExit,
        RuntimeError,
        ConnectionError,
        RecursionError,
        asyncio.CancelledError,
    ):
        pass
    except (ModuleNotFoundError, ImportError) as e:
        LOGS.exception("[MAIN_MODULE_IMPORT] : {}".format(e))
        sys.exit(1)
    except Exception as e:
        LOGS.exception("[MAIN_ERROR] : {}".format(e))
    finally:
        LOGS.info("[MAIN] - App Stopped...")
        sys.exit(0)
