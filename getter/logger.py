# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import logging
import sys
from datetime import UTC, datetime

from loguru import logger as LOG

LOG.remove()
LOG.add(
    f"logs/getter-{datetime.now(UTC):%Y-%m-%d}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    backtrace=False,
    diagnose=False,
    enqueue=True,
    catch=True,
    rotation="3 MB",
    retention="7 days",
    delay=True,
)
LOG.add(
    sys.stdout,
    level="INFO",
    format="{time:MM-DD HH:mm:ss} | {level:<8} | {message}",
    filter=lambda r: r["level"].name != "ERROR",
    colorize=False,
    backtrace=False,
    diagnose=False,
    enqueue=True,
    catch=True,
)
LOG.add(
    sys.stderr,
    level="ERROR",
    format="{time:MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} | {message}",
    colorize=False,
    backtrace=False,
    diagnose=False,
    enqueue=True,
    catch=True,
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
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
for name in (
    "asyncio",
    "telethon",
    "telethon.network.mtprotosender",
    "pytgcalls",
):
    logging.getLogger(name).setLevel(logging.ERROR)
