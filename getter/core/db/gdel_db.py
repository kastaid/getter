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

_GDEL_CACHE = TTLCache(maxsize=100, ttl=30)  # 30 sec


class GDel(Model):
    __tablename__ = "gdel"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)


async def all_gdel() -> list[GDel]:
    async with Session() as s:
        try:
            return (await s.execute(select(GDel).order_by(GDel.date.asc()))).scalars().all()
        except BaseException:
            return []


async def gdel_list() -> list[dict[str, Any]]:
    return [i.to_dict() for i in await all_gdel()]


async def is_gdel(
    user_id: int,
    use_cache: bool = False,
) -> GDel | None:
    user_id, value = str(user_id), None
    if use_cache and user_id in _GDEL_CACHE:
        return _GDEL_CACHE.get(user_id)
    async with Session() as s:
        try:
            data = (await s.execute(select(GDel).filter(GDel.user_id == user_id))).scalar_one_or_none()
            if data:
                await s.refresh(data)
                value = data
                if use_cache and not _GDEL_CACHE.get(user_id):
                    _GDEL_CACHE[user_id] = value
            return value
        except BaseException:
            pass
        return value


async def add_gdel(
    user_id: int,
    date: float,
    reason: str = "",
) -> None:
    async with Session(True) as s:
        await s.execute(
            insert(GDel).values(
                user_id=str(user_id),
                date=date,
                reason=reason,
            ),
        )


async def del_gdel(user_id: int) -> None:
    async with Session(True) as s:
        user_id = str(user_id)
        if user_id in _GDEL_CACHE:
            del _GDEL_CACHE[user_id]
        await s.execute(delete(GDel).where(GDel.user_id == user_id))


async def set_gdel_reason(
    user_id: int,
    reason: str = "",
) -> str:
    gdel = await is_gdel(user_id)
    if not gdel:
        return ""
    async with Session(True) as s:
        prev_reason = gdel.reason
        gdel.reason = reason
        await s.merge(gdel)
        return prev_reason
