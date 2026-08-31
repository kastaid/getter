# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Float,
    UnicodeText,
    delete,
    insert,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB

from .connector import Model, Session


class GoAFK(Model):
    __tablename__ = "afk"
    state = Column(Boolean, primary_key=True)
    reason = Column(UnicodeText)
    start = Column(Float)
    last = Column(JSON().with_variant(JSONB, "postgresql"))


async def is_afk() -> GoAFK | None:
    async with Session() as s:
        try:
            return (await s.execute(select(GoAFK).filter(GoAFK.state))).scalar_one_or_none()
        except BaseException:
            pass


async def add_afk(
    reason: str,
    start: float,
) -> None:
    await del_afk()
    async with Session(True) as s:
        await s.execute(
            insert(GoAFK).values(
                state=True,
                reason=reason,
                start=start,
                last={},
            )
        )


async def del_afk():
    if not await is_afk():
        return
    async with Session(True) as s:
        await s.execute(delete(GoAFK).where(GoAFK.state))


async def set_last_afk(
    chat_id: str,
    msg_id: int,
) -> dict[str, Any]:
    afk = await is_afk()
    if not afk:
        return {}
    async with Session(True) as s:
        old_last = afk.last
        afk.last = {**old_last, chat_id: msg_id}
        await s.merge(afk)
        return old_last
