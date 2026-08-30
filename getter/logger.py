# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import logging
import sys

from loguru import logger as LOG

from . import LOG_DIR
from .config import Var

LOG.remove()
LOG.add(
    LOG_DIR / "getter.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    backtrace=Var.DEV_MODE,
    diagnose=Var.DEV_MODE,
    enqueue=True,
    catch=True,
    rotation="3 MB",
    retention=5,
    delay=True,
)
LOG.add(
    sys.stdout,
    level="INFO",
    format="{time:MM-DD HH:mm:ss} | {level:<8} | {message}",
    filter=lambda r: r["level"].no < 30,
    colorize=Var.DEV_MODE,
    backtrace=False,
    diagnose=False,
    enqueue=True,
    catch=True,
)
LOG.add(
    sys.stderr,
    level="WARNING",
    format="{time:MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    colorize=Var.DEV_MODE,
    backtrace=Var.DEV_MODE,
    diagnose=Var.DEV_MODE,
    enqueue=True,
    catch=True,
)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = LOG.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame = sys._getframe(2)
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        LOG.opt(
            exception=record.exc_info,
            lazy=True,
            depth=depth,
        ).log(level, record.getMessage())


logging.basicConfig(
    handlers=[InterceptHandler()],
    level=logging.INFO,
    force=True,
)
logging.disable(logging.DEBUG)

if not Var.DEV_MODE:
    for name in (
        "telethon",
        "telethon.network.mtprotosender",
        "pytgcalls",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
    for name in (
        "telethon.network.connection.connection",
        "telethon.client.messageparse",
        "telethon.client.users",
        "telethon.client.updates",
    ):
        logging.getLogger(name).setLevel(logging.ERROR)
