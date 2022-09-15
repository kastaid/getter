# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from telethon.tl import types as typ
from . import (
    LOGS,
    getter_app,
    events,
    suppress,
    mentionuser,
    display_name,
    humanbool,
    is_gban,
    is_gmute,
    is_gdel,
    is_allow,
)

gbanned_text = r"""
\\<b>#GBanned_Watch</b>// User  {}  joined and banned!
<b>Reported:</b> <code>{}</code>
<b>Reason:</b> {}
"""
gmuted_text = r"""
\\<b>#GMuted_Watch</b>// User  {}  joined and muted!
<b>Reason:</b> {}
"""


@getter_app.on(events.NewMessage(incoming=True, func=lambda e: e.is_private or e.is_group))
async def OnNewMessageFunc(kst):
    try:
        await DeletedUserHandler(kst)
    except ConnectionError:
        pass
    except Exception as err:
        LOGS.exception(err)


@getter_app.on(events.ChatAction(func=lambda e: e.user_joined or e.user_added))
async def OnChatActionFunc(kst):
    try:
        await JoinedHandler(kst)
    except ConnectionError:
        pass
    except Exception as err:
        LOGS.exception(err)


async def DeletedUserHandler(kst):
    user = await kst.get_sender()
    if not isinstance(user, typ.User):
        return
    if kst.is_private and is_allow(user.id, use_cache=True):
        return
    if is_gdel(user.id, use_cache=True):
        with suppress(BaseException):
            await kst.delete()


async def JoinedHandler(kst):
    ga = kst.client
    chat = await kst.get_chat()
    if not (chat.admin_rights or chat.creator):
        return
    user = await kst.get_user()
    gban = is_gban(user.id, use_cache=True)
    if gban:
        is_reported = bool(await ga.report_spam(user.id))
        if kst.is_group:
            await kst.reply(
                gbanned_text.format(
                    mentionuser(user.id, display_name(user), sep="➥ ", width=15, html=True),
                    humanbool(is_reported),
                    f"<pre>{gban.reason}</pre>" if gban.reason else "No reason.",
                ),
                parse_mode="html",
                silent=True,
            )
        with suppress(BaseException):
            await ga.edit_permissions(chat.id, user.id, view_messages=False)
    gmute = is_gmute(user.id, use_cache=True)
    if gmute and kst.is_group:
        await kst.reply(
            gmuted_text.format(
                mentionuser(user.id, display_name(user), sep="➥ ", width=15, html=True),
                f"<pre>{gmute.reason}</pre>" if gmute.reason else "No reason.",
            ),
            parse_mode="html",
            silent=True,
        )
        with suppress(BaseException):
            await ga.edit_permissions(chat.id, user.id, send_messages=False)
