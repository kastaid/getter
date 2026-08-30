# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import orjson
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

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        return orjson.dumps(self.to_dict()).decode()

    @classmethod
    def from_json(cls, json_data):
        return cls(**orjson.loads(json_data))

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.to_dict()})"


async def db_connect() -> AsyncEngine:
    if hasattr(db_connect, "engine"):
        return db_connect.engine
    db_url = Var.DATABASE_URL
    if db_url.startswith("sqlite"):
        name = Path(db_url.rsplit("/", 1)[-1]).name
        db_url = f"sqlite+aiosqlite:///{DB_DIR / name}"
    elif db_url.startswith(("postgres:", "postgresql:")):
        db_url = db_url.replace(db_url.split("://")[0], "postgresql+asyncpg")
    engine = create_async_engine(
        db_url,
        echo=False,
        json_deserializer=orjson.loads,
        json_serializer=lambda x: orjson.dumps(x).decode(),
    )
    try:
        async with engine.connect() as conn:
            LOG.success("Database connected.")
        async with engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all, checkfirst=True)
            LOG.success("Tables created.")
    except Exception:
        LOG.exception("Unable to connect the database.")
        await engine.dispose()
        sys.exit(1)
    db_connect.engine = engine
    return engine


async def db_disconnect() -> None:
    db = await db_connect()
    await db.dispose()


async def db_size() -> int:
    db = await db_connect()
    url = str(db.url)
    async with db.connect() as conn:
        if "postgresql" in url:
            d = url.rsplit("/", maxsplit=1)[-1].split("?", maxsplit=1)[0]
            q = f"SELECT pg_database_size({d!r})"
        else:
            q = "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
        return (await conn.execute(text(q))).scalar()


@asynccontextmanager
async def Session(commit: bool = False) -> AsyncIterator[AsyncSession]:
    if not hasattr(Session, "cached_session"):
        Session.cached_session = async_sessionmaker(
            await db_connect(),
            expire_on_commit=True,
            autocommit=False,
        )
    async with Session.cached_session() as session:
        if commit:
            async with session.begin():
                yield session
        else:
            yield session
