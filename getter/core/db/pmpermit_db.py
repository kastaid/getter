# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from cachetools import LRUCache
from sqlalchemy import (
    Column,
    Float,
    String,
    UnicodeText,
    delete,
    insert,
    select,
)

from .engine import Model, Session

_PMPERMIT_CACHE = LRUCache(maxsize=100)


class PMPermit(Model):
    __tablename__ = "pmpermit"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)


async def all_allow() -> list[PMPermit]:
    async with Session() as s:
        try:
            return (await s.execute(select(PMPermit).order_by(PMPermit.date.asc()))).scalars().all()
        except BaseException:
            return []


async def is_allow(
    user_id: int,
    use_cache: bool = False,
) -> PMPermit | None:
    user_id, value = str(user_id), None
    if use_cache and user_id in _PMPERMIT_CACHE:
        return _PMPERMIT_CACHE.get(user_id)
    async with Session() as s:
        try:
            data = (await s.execute(select(PMPermit).filter(PMPermit.user_id == user_id))).scalar_one_or_none()
            if data:
                await s.refresh(data)
                value = data
                if use_cache and not _PMPERMIT_CACHE.get(user_id):
                    _PMPERMIT_CACHE[user_id] = value
            return value
        except BaseException:
            pass
        return value


async def allow_user(
    user_id: int,
    date: float,
    reason: str = "",
) -> None:
    async with Session(True) as s:
        await s.execute(
            insert(PMPermit).values(
                user_id=str(user_id),
                date=date,
                reason=reason,
            ),
        )


async def deny_user(user_id: int) -> None:
    async with Session(True) as s:
        user_id = str(user_id)
        if user_id in _PMPERMIT_CACHE:
            del _PMPERMIT_CACHE[user_id]
        await s.execute(delete(PMPermit).where(PMPermit.user_id == user_id))


async def deny_all() -> None:
    async with Session(True) as s:
        await s.execute(delete(PMPermit))
