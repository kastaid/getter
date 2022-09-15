# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_GVAR_CACHE = LRUCache(maxsize=1024)
_GLOBALS_LOCK = RLock()


class Globals(BASE):
    __tablename__ = "globals"
    var = Column(String, primary_key=True, nullable=False)
    value = Column(UnicodeText, primary_key=True, nullable=False)

    def __init__(self, var, value):
        self.var = str(var)
        self.value = value

    def __repr__(self):
        return "<Database.Globals:\n var: {}\n value: {}\n>".format(
            self.var,
            self.value,
        )

    def to_dict(self):
        return {
            "var": self.var,
            "value": self.value,
        }


Globals.__table__.create(checkfirst=True)


def gvar(var, use_cache: bool = False):
    var, value = str(var), None
    if use_cache and var in _GVAR_CACHE:
        return _GVAR_CACHE.get(var)
    try:
        data = SESSION.query(Globals).filter(Globals.var == var).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data.value
            if use_cache and not _GVAR_CACHE.get(var):
                _GVAR_CACHE[var] = value
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def sgvar(var, value):
    with _GLOBALS_LOCK:
        var = str(var)
        if SESSION.query(Globals).filter(Globals.var == var).one_or_none():
            dgvar(var)
        SESSION.add(Globals(var, value))
        SESSION.commit()


def dgvar(var):
    with _GLOBALS_LOCK:
        var = str(var)
        done = SESSION.query(Globals).filter(Globals.var == var).delete(synchronize_session="fetch")
        if done:
            SESSION.commit()


def all_gvar():
    try:
        return SESSION.query(Globals).order_by(Globals.var.asc()).all()
    except BaseException:
        return []
    finally:
        SESSION.close()


def gvar_list():
    try:
        return [x.to_dict() for x in all_gvar()]
    except BaseException:
        return []
    finally:
        SESSION.close()
