# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from collections import UserDict
from html import escape
from typing import Any

from cachetools import LRUCache, cached
from heroku3 import from_key

from getter.config import BOTLOGS_CACHE, Var
from getter.logger import LOG

from .db import get_col, gvar
from .utils import get_full_class_name


class PluginsHelp(UserDict):
    def append(self, obj: dict) -> None:
        plug = next(iter(obj.keys()))
        cmds = {}
        for i in obj[plug]:
            name = next(iter(i.keys()))
            desc = i[name]
            cmds[name] = desc
        self[plug] = cmds

    @property
    def count(self) -> int:
        return len(self)

    @property
    def total(self) -> int:
        return sum(len(i) for i in self.values())


class JSONData:
    def __init__(self) -> None:
        self.CACHE_DATA = LRUCache(maxsize=float("inf"))

    async def sudos(self) -> dict[str, Any]:
        return getattr(await get_col("sudos"), "json", {})

    async def pmwarns(self) -> dict[str, int]:
        return getattr(await get_col("pmwarns"), "json", {})

    async def pmlasts(self) -> dict[str, int]:
        return getattr(await get_col("pmwarns"), "njson", {})

    async def gblack(self) -> dict[str, Any]:
        return getattr(await get_col("gblack"), "json", {})

    async def gblacklist(self) -> set[int]:
        result = await self.gblack()
        return {int(i) for i in result}

    async def sudo_users(self) -> list[int]:
        if "sudo" in self.CACHE_DATA:
            return self.CACHE_DATA.get("sudo", [])
        result = await self.sudos()
        users = [int(i) for i in result]
        if "sudo" not in self.CACHE_DATA:
            self.CACHE_DATA["sudo"] = users
        return users


class Heroku:
    def __init__(self) -> None:
        self.name: str = Var.HEROKU_APP_NAME
        self.api: str = Var.HEROKU_API

    def heroku(self) -> Any:
        conn = None
        try:
            if self.is_heroku:
                conn = from_key(self.api)
        except BaseException as err:
            LOG.exception(err)
        return conn

    @property
    @cached(LRUCache(maxsize=512))
    def stack(self) -> str:
        try:
            app = self.heroku().app(self.name)
            stack = app.info.stack.name
        except BaseException:
            stack = "none"
        return stack

    @property
    def is_heroku(self) -> bool:
        return bool(self.api and self.name)


async def get_botlogs() -> int:
    if BOTLOGS_CACHE:
        return next(reversed(BOTLOGS_CACHE), 0)
    b = await gvar("BOTLOGS", use_cache=True)
    i = int(Var.BOTLOGS or b or 0)
    BOTLOGS_CACHE.append(i)
    return i


def formatx_send(err: Exception) -> str:
    text = r"\\<b>#Getter_Error</b>//"
    text += f"\n<pre>{get_full_class_name(err)}: {escape(str(err))}</pre>"
    return text


plugins_help = PluginsHelp()
jdata = JSONData()
hk = Heroku()
