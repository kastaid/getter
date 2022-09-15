# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import sys
from threading import RLock
from time import perf_counter
from cachetools import LRUCache, TTLCache
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import *
from sqlalchemy_json import MutableJson, NestedMutableJson
from ...config import Var
from ...logger import LOGS

db_url = Var.DATABASE_URL.replace("postgres:", "postgresql:") if "postgres://" in Var.DATABASE_URL else Var.DATABASE_URL


def start() -> scoped_session:
    engine = create_engine(url=db_url)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


try:
    BASE = declarative_base()
    SESSION = start()
except Exception as err:
    LOGS.exception(f"Failed to connect db: {err}")
    sys.exit(1)
