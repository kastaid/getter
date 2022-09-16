# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_GMUTE_CACHE = TTLCache(maxsize=1024, ttl=60, timer=perf_counter)  # 1 mins
_GMUTE_LOCK = RLock()


class GMute(BASE):
    __tablename__ = "gmute"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)

    def __init__(self, user_id, date, reason):
        self.user_id = str(user_id)
        self.date = date
        self.reason = reason

    def __repr__(self):
        return "<Database.GMute:\n user_id: {}\n date: {}\n reason: {}\n>".format(
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


GMute.__table__.create(checkfirst=True)


def is_gmute(user_id, use_cache: bool = False):
    user_id, value = str(user_id), None
    if use_cache and user_id in _GMUTE_CACHE:
        return _GMUTE_CACHE.get(user_id)
    try:
        data = SESSION.query(GMute).filter(GMute.user_id == user_id).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data
            if use_cache and not _GMUTE_CACHE.get(user_id):
                _GMUTE_CACHE[user_id] = value
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def add_gmute(user_id, date, reason=None):
    with _GMUTE_LOCK:
        user_id = str(user_id)
        SESSION.add(GMute(user_id, date, reason or ""))
        SESSION.commit()


def del_gmute(user_id):
    with _GMUTE_LOCK:
        user_id = str(user_id)
        user = SESSION.query(GMute).get(user_id)
        if user:
            SESSION.delete(user)
            SESSION.commit()


def set_gmute_reason(user_id, reason):
    with _GMUTE_LOCK:
        user_id = str(user_id)
        user = SESSION.query(GMute).get(user_id)
        if not user:
            return ""
        prev_reason = user.reason
        user.reason = reason
        SESSION.merge(user)
        SESSION.commit()
        return prev_reason


def all_gmute():
    try:
        return SESSION.query(GMute).order_by(GMute.date.asc()).all()
    except BaseException:
        return []
    finally:
        SESSION.close()


def gmute_list():
    try:
        return [x.to_dict() for x in all_gmute()]
    except BaseException:
        return []
    finally:
        SESSION.close()
