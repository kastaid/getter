# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from typing import Any

from sqlalchemy import (
    Column,
    String,
    delete,
    exists,
    insert,
    select,
    update,
)
from sqlalchemy_json import MutableJson, NestedMutableJson

from .engine import Model, Session


class Collections(Model):
    __tablename__ = "collections"
    keyword = Column(String, primary_key=True)
    json = Column(MutableJson)
    njson = Column(NestedMutableJson)


async def get_cols() -> list[Collections]:
    async with Session() as s:
        try:
            return (await s.execute(select(Collections).order_by(Collections.keyword.asc()))).scalars().all()
        except BaseException:
            return []


async def col_list() -> list[dict[str, Any]]:
    return [i.to_dict() for i in await get_cols()]


async def get_col(keyword: str) -> Collections:
    async with Session() as s:
        try:
            data = (await s.execute(select(Collections).filter(Collections.keyword == keyword))).scalar_one_or_none()
            if data:
                await s.refresh(data)
                return data
        except BaseException:
            pass
        return {}


async def set_col(
    keyword: str,
    json: Any,
    njson: Any = None,
) -> None:
    njson = njson or {}
    async with Session(True) as s:
        data = await s.execute(select(exists().where(Collections.keyword == keyword)))
        if data.scalar():
            stmt = (
                update(Collections)
                .where(Collections.keyword == keyword)
                .values(
                    json=json,
                    njson=njson,
                )
            )
        else:
            stmt = insert(Collections).values(
                keyword=keyword,
                json=json,
                njson=njson,
            )
        await s.execute(stmt)


async def del_col(keyword: str) -> None:
    async with Session(True) as s:
        await s.execute(delete(Collections).where(Collections.keyword == keyword))
