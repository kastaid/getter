# ruff: noqa: F401, F403
# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

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
