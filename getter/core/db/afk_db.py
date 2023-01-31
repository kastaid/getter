# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_GOAFK_LOCK = RLock()


class GoAFK(BASE):
    __tablename__ = "afk"
    state = Column(Boolean, primary_key=True)
    reason = Column(UnicodeText)
    start = Column(Float)
    last = Column(MutableJson)  # MutableDict.as_mutable(JSON)

    def __init__(self, state, reason, start, last):
        self.state = state
        self.reason = reason
        self.start = start
        self.last = last

    def __repr__(self):
        return "<Database.GoAFK:\n state: {}\n reason: {}\n start: {}\n last: {}\n>".format(
            self.state,
            self.reason,
            self.start,
            self.last,
        )

    def to_dict(self):
        return {
            "state": self.state,
            "reason": self.reason,
            "start": self.start,
            "last": self.last,
        }


GoAFK.__table__.create(checkfirst=True)


def is_afk():
    state, value = True, None
    try:
        data = SESSION.query(GoAFK).filter(GoAFK.state == state).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def add_afk(reason, start):
    with _GOAFK_LOCK:
        afk = SESSION.query(GoAFK).get(True)
        if afk:
            SESSION.delete(afk)
        SESSION.add(GoAFK(True, reason, start, {}))
        SESSION.commit()


def del_afk():
    with _GOAFK_LOCK:
        afk = SESSION.query(GoAFK).get(True)
        if afk:
            SESSION.delete(afk)
            SESSION.commit()


def set_last_afk(chat_id, msg_id):
    with _GOAFK_LOCK:
        afk = SESSION.query(GoAFK).get(True)
        if not afk:
            return {}
        old_last = afk.last
        afk.last[chat_id] = msg_id
        SESSION.merge(afk)
        SESSION.commit()
        return old_last
