# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import datetime
import logging
import sys
from loguru import logger as LOGS

LOGS.remove(0)
LOGS.add(
    "logs/getter-{}.log".format(datetime.date.today().strftime("%d-%m-%Y")),
    format="{time:DD/MM/YY HH:mm:ss} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} : {message}",
    rotation="1 days",
    encoding="utf8",
)
LOGS.add(
    sys.stderr,
    format="{time:DD/MM/YY HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    colorize=False,
)
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


logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("urllib3").disabled = True
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.basicConfig(handlers=[InterceptHandler()], level="INFO")
