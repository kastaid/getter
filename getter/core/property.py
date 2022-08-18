# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import re
import sys
from base64 import b64decode
from typing import Union, List, Set
from cache import AsyncTTL
from .. import __license__, __copyright__
from ..logger import LOGS
from .functions import Searcher

Props = Union[List[Union[int, str]], Set[Union[int, str]]]

_c, _u, _g, _v = (
    b64decode("a2FzdGFpZA==").decode("utf-8"),
    b64decode("a2FzdGF1cA==").decode("utf-8"),
    b64decode("a2FzdGFvdA==").decode("utf-8"),
    b64decode("dG9uZ2tyb25nYW52aXJ0dWFscw==").decode("utf-8"),
)


def do_not_remove_credit() -> None:
    if _c not in __copyright__:
        LOGS.warning(__copyright__)
        LOGS.warning("PLEASE RESPECT US, DO NOT REMOVE THE ORIGINAL CREDITS AND LICENSE !!")
        LOGS.warning(__license__)
        sys.exit(1)


@AsyncTTL(time_to_live=(120 * 30), maxsize=1024)  # 1 hours
async def get_blacklisted(
    url: str,
    is_json: bool = False,
    attempts: int = 3,
    fallbacks: Props = [],
) -> Props:
    count = 0
    is_content = False if is_json else True
    while count < attempts:
        res = await Searcher(
            url=url,
            re_json=is_json,
            re_content=is_content,
        )
        count += 1
        if not res:
            if count != attempts:
                await asyncio.sleep(1)
                continue
            ids = fallbacks
            break
        if is_content:
            _ = r"(\[|\]|\{|\}|#.[\w]*|,)"
            ids = {int(x) for x in re.sub(_, " ", "".join(res.decode("utf-8").split())).split()}
        else:
            ids = set(res)
        break
    return ids
