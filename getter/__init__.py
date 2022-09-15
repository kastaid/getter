# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import sys
from pathlib import Path
from platform import python_version
from shutil import rmtree
from time import time
from telethon.tl.alltlobjects import LAYER as __layer__
from telethon.version import __version__ as __tlversion__
from version import __version__

StartTime = time()
__license__ = "GNU Affero General Public License v3.0"
__copyright__ = "Getter Copyright (C) 2022 kastaid"
__pyversion__ = python_version()

if not sys.platform.startswith("linux"):
    print(f"You must use Linux platform, currently {sys.platform}. Quitting...")
    sys.exit(1)
if "/com.termux" in sys.executable:
    print("You are detected using Termux, maybe the functionality will not work normally.")
if sys.version_info < (3, 9, 0):
    print(f"You must use at least Python version 3.9.0, currently {__pyversion__}. Quitting...")
    sys.exit(1)

Root: Path = Path(__file__).parent.parent
DIRS = ["logs/", "downloads/"]
for d in DIRS:
    if not (Root / d).exists():
        (Root / d).mkdir(parents=True, exist_ok=True)
    else:
        for _ in (Root / d).rglob("*"):
            if _.is_dir():
                rmtree(_)
            else:
                _.unlink(missing_ok=True)
[_.unlink(missing_ok=True) for _ in Root.rglob("*s_list.csv")]

del sys, Path, python_version, rmtree, time
