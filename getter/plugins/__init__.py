# ruff: noqa: F401, F403
# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from validators.url import url as is_url

from getter import (
    Root,
    StartTime,
    __copyright__,
    __layer__,
    __license__,
    __pyversion__,
    __tlversion__,
    __version__,
)
from getter.config import *
from getter.core import *
from getter.logger import LOG
