# type: ignore
# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from .engine import *

_COLLECTIONS_LOCK = RLock()


class Collections(BASE):
    __tablename__ = "collections"
    keyword = Column(String, primary_key=True)
    json = Column(MutableJson)
    njson = Column(NestedMutableJson)

    def __init__(self, keyword, json, njson):
        self.keyword = keyword
        self.json = json
        self.njson = njson

    def __repr__(self):
        return "<Database.Collections:\n keyword: {}\n json: {}\n njson: {}\n>".format(
            self.keyword,
            self.json,
            self.njson,
        )

    def to_dict(self):
        return {
            "keyword": self.keyword,
            "json": self.json,
            "njson": self.njson,
        }


Collections.__table__.create(checkfirst=True)


def get_col(keyword):
    value = None
    try:
        data = SESSION.query(Collections).filter(Collections.keyword == keyword).one_or_none()
        if data:
            SESSION.refresh(data)
            value = data
        return value
    except BaseException:
        return value
    finally:
        SESSION.close()


def add_col(keyword, json, njson=None):
    with _COLLECTIONS_LOCK:
        items = SESSION.query(Collections).get(keyword)
        if items:
            SESSION.delete(items)
        SESSION.add(Collections(keyword, json, njson or {}))
        SESSION.commit()


def del_col(keyword):
    with _COLLECTIONS_LOCK:
        items = SESSION.query(Collections).get(keyword)
        if items:
            SESSION.delete(items)
            SESSION.commit()


def get_cols():
    try:
        return SESSION.query(Collections).order_by(Collections.keyword.asc()).all()
    except BaseException:
        return []
    finally:
        SESSION.close()


def col_list():
    try:
        return [x.to_dict() for x in get_cols()]
    except BaseException:
        return []
    finally:
        SESSION.close()
