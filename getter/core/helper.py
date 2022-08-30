# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from cachetools import cached, LRUCache
from heroku3 import from_key
from ..config import Var
from ..logger import LOGS


class PluginsHelpDict(dict):
    def append(self, obj: dict):
        plugin_name = list(obj.keys())[0]
        cmds = obj[plugin_name]
        commands = {}
        for x in cmds:
            name = list(x.keys())[0]
            desc = x[name]
            commands[name] = desc
        self[plugin_name] = commands


class Heroku:
    def __init__(self):
        self.name = Var.HEROKU_APP_NAME
        self.api = Var.HEROKU_API

    def heroku(self) -> None:
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


plugins_help = PluginsHelpDict()
Hk = Heroku()
