# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_PMPERMIT_CACHE = LRUCache(maxsize=1024)
_PMPERMIT_LOCK = RLock()


class PMPermit(BASE):
    __tablename__ = "pmpermit"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)

    def __init__(self, user_id, date, reason):
        self.user_id = str(user_id)
        self.date = date
        self.reason = reason

    def __repr__(self):
        return "<Database.PMPermit:\n user_id: {}\n date: {}\n reason: {}\n>".format(
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


PMPermit.__table__.create(checkfirst=True)


def is_allow(user_id, use_cache: bool = False):
    user_id, value = str(user_id), None
    if use_cache and user_id in _PMPERMIT_CACHE:
        return _PMPERMIT_CACHE.get(user_id)
    try:
        data = SESSION.query(PMPermit).filter(PMPermit.user_id == user_id).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data
            if use_cache and not _PMPERMIT_CACHE.get(user_id):
                _PMPERMIT_CACHE[user_id] = value
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def allow_user(user_id, date, reason=None):
    with _PMPERMIT_LOCK:
        user_id = str(user_id)
        SESSION.add(PMPermit(user_id, date, reason or ""))
        SESSION.commit()


def deny_user(user_id):
    with _PMPERMIT_LOCK:
        user_id = str(user_id)
        user = SESSION.query(PMPermit).get(user_id)
        if user:
            SESSION.delete(user)
            SESSION.commit()


def all_allow():
    try:
        return SESSION.query(PMPermit).order_by(PMPermit.date.asc()).all()
    except BaseException:
        return []
    finally:
        SESSION.close()


def deny_all():
    try:
        SESSION.query(PMPermit).delete()
        SESSION.commit()
        return True
    except BaseException:
        return False
    finally:
        SESSION.close()
