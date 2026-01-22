# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from typing import Any

from cachetools import TTLCache
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

_GBAN_CACHE = TTLCache(maxsize=100, ttl=60)  # 1 mins


class GBan(Model):
    __tablename__ = "gban"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)


async def all_gban() -> list[GBan]:
    async with Session() as s:
        try:
            return (await s.execute(select(GBan).order_by(GBan.date.asc()))).scalars().all()
        except BaseException:
            return []


async def gban_list() -> list[dict[str, Any]]:
    return [i.to_dict() for i in await all_gban()]


async def is_gban(
    user_id: int,
    use_cache: bool = False,
) -> GBan | None:
    user_id, value = str(user_id), None
    if use_cache and user_id in _GBAN_CACHE:
        return _GBAN_CACHE.get(user_id)
    async with Session() as s:
        try:
            data = (await s.execute(select(GBan).filter(GBan.user_id == user_id))).scalar_one_or_none()
            if data:
                await s.refresh(data)
                value = data
                if use_cache and not _GBAN_CACHE.get(user_id):
                    _GBAN_CACHE[user_id] = value
            return value
        except BaseException:
            pass
        return value


async def add_gban(
    user_id: int,
    date: float,
    reason: str = "",
) -> None:
    async with Session(True) as s:
        await s.execute(
            insert(GBan).values(
                user_id=str(user_id),
                date=date,
                reason=reason,
            ),
        )


async def del_gban(user_id: int) -> None:
    async with Session(True) as s:
        user_id = str(user_id)
        if user_id in _GBAN_CACHE:
            del _GBAN_CACHE[user_id]
        await s.execute(delete(GBan).where(GBan.user_id == user_id))


async def set_gban_reason(
    user_id: int,
    reason: str = "",
) -> str:
    gban = await is_gban(user_id)
    if not gban:
        return ""
    async with Session(True) as s:
        prev_reason = gban.reason
        gban.reason = reason
        await s.merge(gban)
        return prev_reason
