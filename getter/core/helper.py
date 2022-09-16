# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import typing
from cachetools import cached, LRUCache
from heroku3 import from_key
from ..config import Var, BOTLOGS_CACHE
from ..logger import LOGS
from .db import gvar, get_col


class PluginsHelp(dict):
    def append(self, obj: dict) -> None:
        plug = list(obj.keys())[0]
        cmds = {}
        for _ in obj[plug]:
            name = list(_.keys())[0]
            desc = _[name]
            cmds[name] = desc
        self[plug] = cmds

    @property
    def count(self) -> int:
        return len(self)

    @property
    def total(self) -> int:
        return sum(len(_) for _ in self.values())


class JSONData:
    def sudos(self) -> typing.Dict[str, typing.Any]:
        return getattr(get_col("sudos"), "json", {})

    def pmwarns(self) -> typing.Dict[str, int]:
        return getattr(get_col("pmwarns"), "json", {})

    def pmlasts(self) -> typing.Dict[str, int]:
        return getattr(get_col("pmwarns"), "njson", {})

    def gblack(self) -> typing.Dict[str, typing.Any]:
        return getattr(get_col("gblack"), "json", {})

    @property
    def gblacklist(self) -> typing.Set[int]:
        return {int(_) for _ in self.gblack()}

    @property
    @cached(LRUCache(maxsize=1024))
    def sudo_users(self) -> typing.List[int]:
        return [int(_) for _ in self.sudos()]


class Heroku:
    def __init__(self) -> None:
        self.name: str = Var.HEROKU_APP_NAME
        self.api: str = Var.HEROKU_API

    def heroku(self) -> typing.Any:
        _conn = None
        try:
            if self.is_heroku:
                _conn = from_key(self.api)
        except BaseException as err:
            LOGS.exception(err)
        return _conn

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


def get_botlogs() -> int:
    if BOTLOGS_CACHE:
        return next((_ for _ in sorted(BOTLOGS_CACHE, reverse=True)), 0)
    nope = int(Var.BOTLOGS or gvar("BOTLOGS", use_cache=True) or 0)
    BOTLOGS_CACHE.add(nope)
    return nope


plugins_help = PluginsHelp()
jdata = JSONData()
hk = Heroku()
