# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import orjson
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.expression import text

from getter import DB_DIR
from getter.config import Var
from getter.logger import LOG

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class Model(DeclarativeBase):
    __abstract__ = True
    __columns_cache__: tuple[str, ...] | None = None

    @classmethod
    def _columns(cls) -> tuple[str, ...]:
        if cls.__columns_cache__ is None:
            cls.__columns_cache__ = tuple(c.key for c in cls.__table__.columns)
        return cls.__columns_cache__

    def to_dict(self) -> dict[str, object]:
        return {k: getattr(self, k) for k in self._columns()}

    def to_json(self) -> str:
        return orjson.dumps(self.to_dict()).decode()

    def __repr__(self) -> str:
        data = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._columns())
        return f"{self.__class__.__name__}({data})"


class State:
    engine: AsyncEngine | None = None
    sessionmaker: async_sessionmaker[AsyncSession] | None = None
    is_sqlite: bool = False


_SQLITE_PRAGMA = (
    "PRAGMA synchronous=NORMAL",
    "PRAGMA busy_timeout=5000",
    "PRAGMA temp_store=MEMORY",
    "PRAGMA cache_size=-2048",
)


def _set_sqlite_pragmas(engine: AsyncEngine) -> None:
    @event.listens_for(engine.sync_engine, "connect")
    def _pragmas(db, _) -> None:
        cursor = db.cursor()
        try:
            for pragma in _SQLITE_PRAGMA:
                cursor.execute(pragma)
        finally:
            cursor.close()


async def database_connect() -> AsyncEngine:
    if State.engine:
        return State.engine
    url = Var.DATABASE_URL
    if not url:
        LOG.error("DATABASE_URL is not set.")
        sys.exit(1)
    if ":memory:" in url:
        LOG.error("In-memory SQLite database is not supported.")
        sys.exit(1)
    if "://" not in url:
        LOG.error("Invalid DATABASE_URL format.")
        sys.exit(1)
    is_sqlite = False
    scheme, rest = url.split("://", 1)
    if scheme in ("sqlite", "sqlite+aiosqlite"):
        name = rest.rsplit("/", 1)[-1]
        url = f"sqlite+aiosqlite:///{DB_DIR / name}"
        is_sqlite = True
    elif scheme in ("postgres", "postgresql"):
        url = f"postgresql+asyncpg://{rest}"
    elif scheme == "postgresql+asyncpg":
        pass
    else:
        LOG.error(f"Unsupported database scheme: {scheme}")
        sys.exit(1)
    engine = create_async_engine(
        url,
        echo=False,
        json_deserializer=orjson.loads,
        json_serializer=lambda v: orjson.dumps(v).decode(),
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=3 if is_sqlite else 5,
        max_overflow=0 if is_sqlite else 2,
    )
    if is_sqlite:
        _set_sqlite_pragmas(engine)
    try:
        async with engine.begin() as db:
            if is_sqlite:
                await db.execute(text("PRAGMA journal_mode=WAL"))
                await db.execute(text("PRAGMA auto_vacuum=INCREMENTAL"))

            await db.run_sync(
                Model.metadata.create_all,
                checkfirst=True,
            )
        LOG.success("DATABASE CONNECTED.")
    except Exception:
        LOG.exception("Unable to connect the database")
        await engine.dispose()
        sys.exit(1)
    State.engine = engine
    State.is_sqlite = is_sqlite
    return engine


async def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if not State.sessionmaker:
        engine = await database_connect()
        State.sessionmaker = async_sessionmaker(
            engine,
            expire_on_commit=False,
            autocommit=False,
        )
    return State.sessionmaker


@asynccontextmanager
async def Session(commit: bool = False) -> AsyncIterator[AsyncSession]:
    sm = await get_sessionmaker()
    if commit:
        async with sm.begin() as session:
            yield session
    else:
        async with sm() as session:
            yield session


async def database_disconnect() -> None:
    if State.engine:
        await State.engine.dispose()
        State.engine = None
        State.sessionmaker = None


async def database_size() -> int:
    engine = await database_connect()
    q = (
        "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
        if State.is_sqlite
        else "SELECT pg_database_size(current_database())"
    )
    async with engine.connect() as db:
        return (await db.execute(text(q))).scalar() or 0
