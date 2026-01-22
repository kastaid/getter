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

_GMUTE_CACHE = TTLCache(maxsize=100, ttl=60)  # 1 mins


class GMute(Model):
    __tablename__ = "gmute"
    user_id = Column(String, primary_key=True)
    date = Column(Float)
    reason = Column(UnicodeText)


async def all_gmute() -> list[GMute]:
    async with Session() as s:
        try:
            return (await s.execute(select(GMute).order_by(GMute.date.asc()))).scalars().all()
        except BaseException:
            return []


async def gmute_list() -> list[dict[str, Any]]:
    return [i.to_dict() for i in await all_gmute()]


async def is_gmute(
    user_id: int,
    use_cache: bool = False,
) -> GMute | None:
    user_id, value = str(user_id), None
    if use_cache and user_id in _GMUTE_CACHE:
        return _GMUTE_CACHE.get(user_id)
    async with Session() as s:
        try:
            data = (await s.execute(select(GMute).filter(GMute.user_id == user_id))).scalar_one_or_none()
            if data:
                await s.refresh(data)
                value = data
                if use_cache and not _GMUTE_CACHE.get(user_id):
                    _GMUTE_CACHE[user_id] = value
            return value
        except BaseException:
            pass
        return value


async def add_gmute(
    user_id: int,
    date: float,
    reason: str = "",
) -> None:
    async with Session(True) as s:
        await s.execute(
            insert(GMute).values(
                user_id=str(user_id),
                date=date,
                reason=reason,
            ),
        )


async def del_gmute(user_id: int) -> None:
    async with Session(True) as s:
        user_id = str(user_id)
        if user_id in _GMUTE_CACHE:
            del _GMUTE_CACHE[user_id]
        await s.execute(delete(GMute).where(GMute.user_id == user_id))


async def set_gmute_reason(
    user_id: int,
    reason: str = "",
) -> str:
    gmute = await is_gmute(user_id)
    if not gmute:
        return ""
    async with Session(True) as s:
        prev_reason = gmute.reason
        gmute.reason = reason
        await s.merge(gmute)
        return prev_reason
