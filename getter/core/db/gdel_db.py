# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_GDEL_CACHE = TTLCache(maxsize=1024, ttl=30, timer=perf_counter)  # 0.5 mins
_GDEL_LOCK = RLock()


class GDel(BASE):
    __tablename__ = "gdel"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)

    def __init__(self, user_id, date, reason):
        self.user_id = str(user_id)
        self.date = date
        self.reason = reason

    def __repr__(self):
        return "<Database.GDel:\n user_id: {}\n date: {}\n reason: {}\n>".format(
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


GDel.__table__.create(checkfirst=True, bind=SESSION)


def is_gdel(user_id, use_cache: bool = False):
    user_id, value = str(user_id), None
    if use_cache and user_id in _GDEL_CACHE:
        return _GDEL_CACHE.get(user_id)
    try:
        data = SESSION.query(GDel).filter(GDel.user_id == user_id).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data
            if use_cache and not _GDEL_CACHE.get(user_id):
                _GDEL_CACHE[user_id] = value
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def add_gdel(user_id, date, reason=None):
    with _GDEL_LOCK:
        user_id = str(user_id)
        SESSION.add(GDel(user_id, date, reason or ""))
        SESSION.commit()


def del_gdel(user_id):
    with _GDEL_LOCK:
        user_id = str(user_id)
        user = SESSION.query(GDel).get(user_id)
        if user:
            SESSION.delete(user)
            SESSION.commit()


def set_gdel_reason(user_id, reason):
    with _GDEL_LOCK:
        user_id = str(user_id)
        user = SESSION.query(GDel).get(user_id)
        if not user:
            return ""
        prev_reason = user.reason
        user.reason = reason
        SESSION.merge(user)
        SESSION.commit()
        return prev_reason


def all_gdel():
    try:
        return SESSION.query(GDel).order_by(GDel.date.asc()).all()
    except BaseException:
        return []
    finally:
        SESSION.close()


def gdel_list():
    try:
        return [x.to_dict() for x in all_gdel()]
    except BaseException:
        return []
    finally:
        SESSION.close()
