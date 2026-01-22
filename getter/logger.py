# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import logging
import sys
from datetime import date

from loguru import logger as LOG

LOG.remove(0)
LOG.add(
    "logs/getter-{}.log".format(date.today().strftime("%Y-%m-%d")),
    format="{time:YY/MM/DD HH:mm:ss} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} : {message}",
    rotation="1 MB",
    enqueue=True,
)
LOG.add(
    sys.stderr,
    format="{time:YY/MM/DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    colorize=False,
)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = LOG.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        LOG.opt(
            exception=record.exc_info,
            lazy=True,
            depth=depth,
        ).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
logging.disable(logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("urllib3").disabled = True
logging.getLogger("urllib3.connectionpool").disabled = True
logging.getLogger("webdriver_manager").disabled = True
logging.getLogger("pytgcalls").setLevel(logging.ERROR)
TelethonLogger = logging.getLogger("telethon")
TelethonLogger.setLevel(logging.ERROR)
