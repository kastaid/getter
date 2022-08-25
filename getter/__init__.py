# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import multiprocessing
import sys
import time
from asyncio import get_event_loop
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from platform import python_version
from shutil import rmtree
from telethon.tl.alltlobjects import LAYER as __layer__
from telethon.version import __version__ as __tlversion__
from version import __version__

StartTime = time.time()
__license__ = "GNU Affero General Public License v3.0"
__copyright__ = "Getter Copyright (C) 2022 kastaid"
__pyversion__ = python_version()

if not sys.platform.startswith("linux"):
    print("You must use Linux platform, currently {}. Quitting...".format(sys.platform))
    sys.exit(1)

if sys.version_info < (3, 9, 0):
    print("You must use at least Python version 3.9.0, currently {}. Quitting...".format(__pyversion__))
    sys.exit(1)

Root: Path = Path(__file__).parent.parent

DIRS = ["logs/", "downloads/"]
for d in DIRS:
    if not (Root / d).exists():
        (Root / d).mkdir(parents=True, exist_ok=True)
    else:
        for p in (Root / d).rglob("*"):
            if p.is_dir():
                rmtree(p)
            else:
                p.unlink(missing_ok=True)

[c.unlink(missing_ok=True) for c in Root.rglob("*s_list.csv")]

LOOP = get_event_loop()
EXECUTOR = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5, thread_name_prefix="Getter")
WORKER = {}
CALLS = {}
TESTER = {5215824623}
# vo, en1, en5, co, xl, ar
DEVS = {
    *{
        int(x)
        for x in b64decode(
            "MjAwMzM2MTQxMCAxOTk4OTE4MDI0IDUxNzcxNjE5NjYgNTE4MDU5NTM5MCAxNDE1OTcxMDIwIDU1MjIzMzY2Mzc="
        ).split()
    },
    *TESTER,
}
MAX_MESSAGE_LEN = 4096
