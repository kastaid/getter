# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from telethon.tl import types as typ
from . import (
    getter_app,
    sendlog,
    events,
    mentionuser,
    display_name,
    humanbool,
    is_gban,
    is_gmute,
    is_gdel,
    is_allow,
)

gbanned_text = r"""
\\<b>#GBanned_Watch</b>// User {} joined and quickly banned!
<b>Reported:</b> <code>{}</code>
<b>Reason:</b> {}
"""
gmuted_text = r"""
\\<b>#GMuted_Watch</b>// User {} joined and quickly muted!
<b>Reason:</b> {}
"""


@getter_app.on(
    events.NewMessage(
        incoming=True,
        func=lambda e: e.is_private or e.is_group,
    )
)
async def OnNewMessageFunc(kst):
    try:
        await DeletedUserHandler(kst)
    except ConnectionError:
        pass
    except Exception as err:
        kst.client.logs.exception(err)


@getter_app.on(
    events.ChatAction(
        func=lambda e: e.user_joined or e.user_added,
    )
)
async def OnChatActionFunc(kst):
    try:
        await JoinedHandler(kst)
    except ConnectionError:
        pass
    except Exception as err:
        kst.client.logs.exception(err)


async def DeletedUserHandler(kst):
    user = await kst.get_sender()
    if not isinstance(user, typ.User):
        return
    if kst.is_private and is_allow(user.id, use_cache=True):
        return
    if is_gdel(user.id, use_cache=True):
        try:
            await kst.delete()
        except BaseException:
            pass


async def JoinedHandler(kst):
    ga = kst.client
    chat = await kst.get_chat()
    if not (chat.admin_rights or chat.creator):
        return
    user = await kst.get_user()
    gban = is_gban(user.id, use_cache=True)
    if gban:
        mention = mentionuser(user.id, display_name(user), width=15, html=True)
        is_reported = await ga.report_spam(user.id)
        logs_text = r"\\<b>#GBanned_Watch</b>//"
        logs_text += f"\nUser {mention} [<code>{user.id}</code>] detected joining chat in <code>{chat.title} - {chat.id}</code> and quickly banned!\n"
        if kst.is_group:
            await kst.reply(
                gbanned_text.format(
                    mention,
                    humanbool(is_reported),
                    f"<pre>{gban.reason}</pre>" if gban.reason else "None given.",
                ),
                parse_mode="html",
                silent=True,
            )
        try:
            await ga.edit_permissions(chat.id, user.id, view_messages=False)
        except BaseException:
            pass
        logs_text += "<b>Reported:</b> <code>{}</code>\n".format(humanbool(is_reported))
        logs_text += "<b>Reason:</b> {}\n".format(f"<pre>{gban.reason}</pre>" if gban.reason else "None given.")
        await sendlog(logs_text)

    gmute = is_gmute(user.id, use_cache=True)
    if gmute and kst.is_group:
        mention = mentionuser(user.id, display_name(user), width=15, html=True)
        logs_text = r"\\<b>#GMuted_Watch</b>//"
        logs_text += f"\nUser {mention} [<code>{user.id}</code>] detected joining chat in <code>{chat.title} - {chat.id}</code> and quickly muted!\n"
        await kst.reply(
            gmuted_text.format(
                mention,
                f"<pre>{gmute.reason}</pre>" if gmute.reason else "None given.",
            ),
            parse_mode="html",
            silent=True,
        )
        try:
            await ga.edit_permissions(chat.id, user.id, send_messages=False)
        except BaseException:
            pass
        logs_text += "<b>Reason:</b> {}\n".format(f"<pre>{gban.reason}</pre>" if gban.reason else "None given.")
        await sendlog(logs_text)
