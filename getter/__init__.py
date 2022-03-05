# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import sys
from asyncio import get_event_loop
from base64 import b64decode
from pathlib import Path
from platform import python_version
from time import time
from version import __version__

StartTime = time()

if not sys.platform.startswith("linux"):
    print("You must use Linux platform, currently {}. Quitting...".format(sys.platform))
    sys.exit(1)

if sys.version_info < (3, 9, 0):
    print("You must use at least Python version 3.9.0, currently {}. Quitting...".format(python_version()))
    sys.exit(1)

Root: Path = Path(__file__).parent.parent

dirs = ["downloads"]
for _ in dirs:
    if not (Root / _).exists():
        (Root / _).mkdir(parents=True, exist_ok=True)
    else:
        for f in (Root / _).rglob("*.*"):
            if f.exists():
                f.unlink(missing_ok=True)

for _ in Root.rglob("*s_list.csv*"):
    _.unlink(missing_ok=True)

LOOP = get_event_loop()
HELP = {}
WORKER = {}
_DEVS = "MjAwMzM2MTQxMCA1MDY4Mzc5NjY3IDUwNzUxMDE2MTAgNTA3MDkxMTI1OSAyMDY5NjQ5MzMw"  # v, e, t, v, c
DEVS = list(map(int, b64decode(_DEVS).decode("utf-8").split()))
del _DEVS
NOCHATS = [
    -1001699144606,  # @kastaot
    -1001700971911,  # @kastaup
]
