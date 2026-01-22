# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from typing import Any

from cachetools import LRUCache
from sqlalchemy import (
    Column,
    String,
    UnicodeText,
    delete,
    exists,
    insert,
    select,
    update,
)

from .engine import Model, Session

_GVAR_CACHE = LRUCache(maxsize=float("inf"))


class Globals(Model):
    __tablename__ = "globals"
    var = Column(String, primary_key=True)
    value = Column(UnicodeText)


async def all_gvar() -> list[Globals]:
    async with Session() as s:
        try:
            return (await s.execute(select(Globals).order_by(Globals.var.asc()))).scalars().all()
        except BaseException:
            return []


async def gvar_list() -> list[dict[str, Any]]:
    return [i.to_dict() for i in await all_gvar()]


async def gvar(
    var: str,
    use_cache: bool = False,
) -> str | None:
    value = None
    if use_cache and var in _GVAR_CACHE:
        return _GVAR_CACHE.get(var)
    async with Session() as s:
        try:
            data = (await s.execute(select(Globals).filter(Globals.var == var))).scalar_one_or_none()
            if data:
                await s.refresh(data)
                value = data.value
                if use_cache and not _GVAR_CACHE.get(var):
                    _GVAR_CACHE[var] = value
        except BaseException:
            pass
        return value


async def sgvar(
    var: str,
    value: str,
) -> None:
    value = str(value)
    async with Session(True) as s:
        data = await s.execute(select(exists().where(Globals.var == var)))
        if data.scalar():
            if var in _GVAR_CACHE:
                del _GVAR_CACHE[var]
            stmt = update(Globals).where(Globals.var == var).values(value=value)
        else:
            stmt = insert(Globals).values(var=var, value=value)
        await s.execute(stmt)


async def dgvar(var: str) -> None:
    async with Session(True) as s:
        if var in _GVAR_CACHE:
            del _GVAR_CACHE[var]
        await s.execute(delete(Globals).where(Globals.var == var))
