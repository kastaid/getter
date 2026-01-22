# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio

from telethon.errors import FloodWaitError

from . import DEVS, kasta_cmd


@kasta_cmd(
    pattern="kickall(?: |$)(.*)",
    admins_only=True,
    require="add_admins",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    opts = kst.pattern_match.group(1).lower()
    rocker = any(_ in opts for _ in ("-s", "silent"))
    if rocker:
        await kst.try_delete()
    else:
        yy = await kst.eor("`Rocker...`")
    success, failed = 0, 0
    async for x in ga.iter_participants(chat_id):
        if not (x.id in DEVS or x.is_self or hasattr(x.participant, "admin_rights")):
            try:
                crying = await ga.edit_permissions(chat_id, x.id, view_messages=False)
                if rocker and crying:
                    cry = [_.id for _ in crying.updates if hasattr(_, "id")]
                    if cry:
                        await ga.delete_messages(chat_id, cry)
                await asyncio.sleep(0.5)
                await ga.edit_permissions(chat_id, x.id)
                await asyncio.sleep(0.5)
                success += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    crying = await ga.edit_permissions(chat_id, x.id, view_messages=False)
                    if rocker and crying:
                        cry = [_.id for _ in crying.updates if hasattr(_, "id")]
                        if cry:
                            await ga.delete_messages(chat_id, cry)
                    await asyncio.sleep(0.5)
                    await ga.edit_permissions(chat_id, x.id)
                    await asyncio.sleep(0.5)
                    success += 1
                except BaseException:
                    failed += 1
            except BaseException:
                failed += 1
    if not rocker:
        await yy.eor(f"👏 **Congratulations +{success}-{failed}**\n__From now, you have no friends!__", time=15)


@kasta_cmd(
    pattern="banall(?: |$)(.*)",
    admins_only=True,
    require="add_admins",
)
async def _(kst):
    ga = kst.client
    chat_id = kst.chat_id
    opts = kst.pattern_match.group(1).lower()
    lucifer = any(_ in opts for _ in ("-s", "silent"))
    if lucifer:
        await kst.try_delete()
    else:
        yy = await kst.eor("`GoHell...`")
    success, failed = 0, 0
    async for x in ga.iter_participants(chat_id):
        if not (x.id in DEVS or x.is_self or hasattr(x.participant, "admin_rights")):
            try:
                crying = await ga.edit_permissions(chat_id, x.id, view_messages=False)
                if lucifer and crying:
                    cry = [_.id for _ in crying.updates if hasattr(_, "id")]
                    if cry:
                        await ga.delete_messages(chat_id, cry)
                await asyncio.sleep(0.5)
                success += 1
            except FloodWaitError as fw:
                await asyncio.sleep(fw.seconds + 10)
                try:
                    crying = await ga.edit_permissions(chat_id, x.id, view_messages=False)
                    if lucifer and crying:
                        cry = [_.id for _ in crying.updates if hasattr(_, "id")]
                        if cry:
                            await ga.delete_messages(chat_id, cry)
                    await asyncio.sleep(0.5)
                    success += 1
                except BaseException:
                    failed += 1
            except BaseException:
                failed += 1
    if not lucifer:
        await yy.eor(f"__You're Lucifer +{success}-{failed}__ 👁️", time=15)
