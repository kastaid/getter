# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_GBAN_CACHE = TTLCache(maxsize=1024, ttl=60, timer=perf_counter)  # 1 mins
_GBAN_LOCK = RLock()


class GBan(BASE):
    __tablename__ = "gban"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)

    def __init__(self, user_id, date, reason):
        self.user_id = str(user_id)
        self.date = date
        self.reason = reason

    def __repr__(self):
        return "<Database.GBan:\n user_id: {}\n date: {}\n reason: {}\n>".format(
            self.user_id,
            self.date,
            self.reason,
        )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "date": self.date,
            "reason": self.reason,
        }


GBan.__table__.create(checkfirst=True)


def is_gban(user_id, use_cache: bool = False):
    user_id, value = str(user_id), None
    if use_cache and user_id in _GBAN_CACHE:
        return _GBAN_CACHE.get(user_id)
    try:
        data = SESSION.query(GBan).filter(GBan.user_id == user_id).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data
            if use_cache and not _GBAN_CACHE.get(user_id):
                _GBAN_CACHE[user_id] = value
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def add_gban(user_id, date, reason=None):
    with _GBAN_LOCK:
        user_id = str(user_id)
        SESSION.add(GBan(user_id, date, reason or ""))
        SESSION.commit()


def del_gban(user_id):
    with _GBAN_LOCK:
        user_id = str(user_id)
        user = SESSION.query(GBan).get(user_id)
        if user:
            SESSION.delete(user)
            SESSION.commit()


def set_gban_reason(user_id, reason):
    with _GBAN_LOCK:
        user_id = str(user_id)
        user = SESSION.query(GBan).get(user_id)
        if not user:
            return ""
        prev_reason = user.reason
        user.reason = reason
        SESSION.merge(user)
        SESSION.commit()
        return prev_reason


def all_gban():
    try:
        return SESSION.query(GBan).order_by(GBan.date.asc()).all()
    except BaseException:
        return []
    finally:
        SESSION.close()


def gban_list():
    try:
        return [x.to_dict() for x in all_gban()]
    except BaseException:
        return []
    finally:
        SESSION.close()
