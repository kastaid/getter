# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from telethon import events
from telethon.tl import types as typ

from . import (
    display_name,
    getter_app,
    humanbool,
    is_allow,
    is_gban,
    is_gdel,
    is_gmute,
    mentionuser,
    sendlog,
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
        kst.client.log.exception(err)


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
        kst.client.log.exception(err)


async def DeletedUserHandler(kst):
    user = await kst.get_sender()
    if not isinstance(user, typ.User):
        return
    if kst.is_private and await is_allow(user.id, use_cache=True):
        return
    if await is_gdel(user.id, use_cache=True):
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
    gban = await is_gban(user.id, use_cache=True)
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
        logs_text += f"<b>Reported:</b> <code>{humanbool(is_reported)}</code>\n"
        logs_text += "<b>Reason:</b> {}\n".format(f"<pre>{gban.reason}</pre>" if gban.reason else "None given.")
        await sendlog(logs_text)

    gmute = await is_gmute(user.id, use_cache=True)
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
