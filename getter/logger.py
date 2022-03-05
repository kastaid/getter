# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import logging
from sys import stderr
from loguru import logger as LOGS
from getter import Root

_log_ = "app.log"
(Root / _log_).unlink(missing_ok=True)

# Logging at the start to catch everything
fmt = "{time:DD/MM/YY, HH:mm:ss} [{level}] || {name}:{line} : {message}"
LOGS.remove(0)
LOGS.add(
    _log_,
    format=fmt,
    rotation="2 days",
    retention="2 days",
    encoding="utf8",
    enqueue=True,
)
LOGS.add(stderr, level="INFO", format=fmt, colorize=False)
LOGS.opt(lazy=True, colors=False)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = LOGS.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        LOGS.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class LogFilter(logging.Filter):
    def filter(self, record):
        if record.funcName == "send":
            return False
        return True


logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("urllib3").disabled = True
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("telethon.network.mtprotosender").addFilter(LogFilter())
logging.basicConfig(handlers=[InterceptHandler()], level="INFO")
