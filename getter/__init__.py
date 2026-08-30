# ruff: noqa: F401
# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import sys
from pathlib import Path
from platform import python_version
from time import monotonic

from telethon.tl.alltlobjects import LAYER as __layer__
from telethon.version import __version__ as __tlversion__

from version import __version__

StartTime = monotonic()
__license__ = "GNU Affero General Public License v3.0"
__copyright__ = "Getter Copyright (C) 2022-present kastaid"
__pyversion__ = python_version()

if not sys.platform.startswith("linux"):
    print(f"You must use Linux platform, currently {sys.platform}. Quitting...")
    sys.exit(1)
if "/com.termux" in sys.executable:
    print("Termux detected. Some functionality may not work properly.")

Root = Path(__file__).parent.parent
LOG_DIR = Root / "logs"
DB_DIR = Root / "db"
DOWNLOAD_DIR = Root / "downloads"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clean_files(path: Path) -> None:
    if not path.exists():
        return
    for i in path.rglob("*"):
        if i.is_file():
            i.unlink(missing_ok=True)


for path in (
    LOG_DIR,
    DB_DIR,
    DOWNLOAD_DIR,
):
    ensure_dir(path)

clean_files(DOWNLOAD_DIR)
