# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from pathlib import Path

Root: Path = Path(__file__).parent.parent

EXTS = (".py", ".yml", ".env")

WAIT_FOR = 1

RST = "\x1b[0m"
BOLD = "\x1b[1m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"
