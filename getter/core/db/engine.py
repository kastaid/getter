# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from orjson import dumps, loads
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.expression import text
from getter.config import Var
from getter.logger import LOG

engine = None


class Model(DeclarativeBase):
    """
    Model is an abstract base class for all SQLAlchemy ORM models ,
    providing common columns and functionality.

    Methods:
        to_dict: Converts the current object to a dictionary.
        to_json: Converts the current object to a JSON string.
        from_json: Creates a new object of the class using the provided JSON data.
        __repr__: Returns a string representation of the current object.
    """

    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        return dumps(self.to_dict()).decode()

    @classmethod
    def from_json(cls, json_data):
        return cls(**loads(json_data))

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.to_dict()})"


async def db_connect() -> AsyncEngine:
    global engine
    if engine is not None:
        return engine
    db_url = (
        Var.DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
        if Var.DATABASE_URL.startswith("sqlite:")
        else Var.DATABASE_URL
    )
    engine = create_async_engine(
        db_url,
        echo=False,
        json_deserializer=loads,
        json_serializer=lambda x: dumps(x).decode(),
    )
    try:
        async with engine.connect() as conn:
            LOG.success("Database connected.")
        async with engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all, checkfirst=True)
            LOG.success("Tables created.")
    except Exception as err:
        LOG.exception(f"Unable to connect the database : {err}")
        await engine.dispose()
        sys.exit(1)
    return engine


async def db_disconnect() -> None:
    db = await db_connect()
    await db.dispose()


async def db_size() -> int:
    db = await db_connect()
    url = str(db.url)
    async with db.connect() as conn:
        if "postgresql" in url:
            d = url.split("/")[-1].split("?")[0]
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
