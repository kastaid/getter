# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from json import loads
from pathlib import Path


def get_version() -> str:
    return loads(Path("manifest.json").read_text()).get("version", "unknown")


__version__ = get_version()
