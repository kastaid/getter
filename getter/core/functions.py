# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import re
import typing
from functools import partial
from textwrap import shorten
from telethon.client.telegramclient import TelegramClient
from telethon.helpers import add_surrogate
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import (
    MessageEntityMentionName,
    MessageEntityPre,
    PeerUser,
    User,
    UserStatusOnline,
    UserStatusOffline,
    UserStatusLastWeek,
    UserStatusLastMonth,
    UserStatusRecently,
)
from telethon.utils import get_display_name
from ..logger import LOGS

TELEGRAM_LINK_RE = r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)([\w-]+)$"
USERNAME_RE = r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)"
MSG_ID_RE = r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)(?:c\/|)(.*)\/(.*)"


def is_telegram_link(url: str) -> bool:
    # TODO: support for username.t.me
    return bool(re.match(TELEGRAM_LINK_RE, url, flags=re.I))


def get_username(url: str) -> str:
    # TODO: support for username.t.me
    return re.sub(USERNAME_RE, "@", url, flags=re.I)


def get_msg_id(link: str) -> typing.Optional[typing.Tuple[typing.Union[str, int]]]:
    # TODO: support for username.t.me
    idx = re.findall(MSG_ID_RE, link, flags=re.I)
    ids = next((_ for _ in idx), None)
    if not ids:
        return None, None
    chat, msg_id = ids
    if chat.isdecimal():
        chat = int("-100" + chat)
    return chat, int(msg_id)


def mentionuser(
    user_id: typing.Union[int, str],
    name: str,
    sep: str = "",
    width: int = 20,
    html: bool = False,
) -> str:
    name = shorten(name, width=width, placeholder="...")
    return f"<a href=tg://user?id={user_id}>{sep}{name}</a>" if html else f"[{sep}{name}](tg://user?id={user_id})"


def display_name(obj) -> str:
    name = get_display_name(obj)
    return name if name else "{}".format(obj.first_name or "none")


def normalize_chat_id(chat_id) -> typing.Union[int, str]:
    if str(chat_id).startswith(("-100", "-")) and str(chat_id)[1:].isdecimal():
        chat_id = int(str(chat_id).replace("-100", "").replace("-", ""))
    elif str(chat_id).isdecimal():
        chat_id = int(chat_id)
    return chat_id


async def get_chat_id(
    kst: TelegramClient,
    group: int = 1,
) -> typing.Optional[int]:
    chat_id = None
    target = await get_text(kst, group=group)
    if not target:
        return int(str(kst.chat_id).replace("-100", "").replace("-", ""))
    target = target.split(" ")[0]
    chat_id = normalize_chat_id(target)
    if isinstance(chat_id, str):
        if is_telegram_link(chat_id):
            chat_id = get_username(chat_id)
        try:
            full = await kst.client(GetFullChatRequest(chat_id))
            chat_id = full.full_chat.id
        except BaseException:
            try:
                full = await kst.client(GetFullChannelRequest(chat_id))
                chat_id = full.full_chat.id
            except BaseException:
                return None
    return chat_id


async def get_text(
    kst: TelegramClient,
    group: int = 1,
    plain: bool = True,
    strip: bool = True,
) -> str:
    match = kst.pattern_match.group(group)
    if kst.is_reply:
        reply = await kst.get_reply_message()
        if not match:
            text = str(reply.message if plain else reply.text)
            if strip:
                text = text.strip()
            return text
    if strip:
        match = match.strip()
    return match


def get_user_status(user: User) -> str:
    if user.bot or user.support:
        status = "none"
    if isinstance(user.status, UserStatusOnline):
        status = "online"
    elif isinstance(user.status, UserStatusOffline):
        status = "offline"
    elif isinstance(user.status, UserStatusRecently):
        status = "recently"
    elif isinstance(user.status, UserStatusLastWeek):
        status = "within_week"
    elif isinstance(user.status, UserStatusLastMonth):
        status = "within_month"
    else:
        status = "long_time_ago"
    return status


async def get_user(
    kst: TelegramClient,
    group: int = 1,
) -> typing.Optional[typing.Tuple[User, str]]:
    args = kst.pattern_match.group(group).strip().split(" ", 1)
    extra = ""
    try:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
                user = int(user)
            if kst.message.entities:
                mention = kst.message.entities[0]
                if isinstance(mention, MessageEntityMentionName):
                    user_id = mention.user_id
                    user_obj = await kst.client.get_entity(PeerUser(user_id))
                    return user_obj, extra
            if isinstance(user, int) or user.startswith("@") or len(user) >= 5:
                user_obj = await kst.client.get_entity(PeerUser(user))
                return user_obj, extra
    except ValueError:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
                await kst.client.get_dialogs()
                obj = partial(type, "User", ())
                user_obj = obj(
                    {
                        "id": int(user),
                        "first_name": user,
                    }
                )
                return user_obj, extra
            return None, None
        return None, None
    except Exception as err:
        LOGS.error(str(err))
    try:
        extra = kst.pattern_match.group(group).strip()
        if kst.is_private:
            user_obj = await kst.get_chat()
            return user_obj, extra
        if kst.is_reply:
            reply = await kst.get_reply_message()
            if reply.from_id is None:
                return None, None
            user_id = reply.sender_id
            try:
                user_obj = await kst.client.get_entity(PeerUser(user_id))
                return user_obj, extra
            except ValueError:
                obj = partial(type, "User", ())
                user_obj = obj(
                    {
                        "id": user_id,
                        "first_name": str(user_id),
                    }
                )
                return user_obj, extra
        if not args:
            return None, None
    except Exception as err:
        LOGS.error(str(err))
    return None, None


async def is_admin(
    kst: TelegramClient,
    chat_id: int,
    user_id: int,
) -> bool:
    try:
        prm = await kst.client.get_permissions(chat_id, user_id)
        if prm.is_admin:
            return True
        return False
    except BaseException:
        return False


async def admin_check(
    kst: TelegramClient,
    chat_id: int,
    user_id: int,
    require: typing.Optional[str] = None,
) -> bool:
    if kst.is_private:
        return True
    try:
        prm = await kst.client.get_permissions(chat_id, user_id)
    except BaseException:
        return False
    if not prm.is_admin:
        return False
    if require and not getattr(prm, require, False):
        return False
    return True


def to_privilege(privilege: str) -> str:
    privileges = {
        "change_info": "can_change_info",
        "post_messages": "can_post_messages",
        "edit_messages": "can_edit_messages",
        "delete_messages": "can_delete_messages",
        "ban_users": "can_restrict_members",
        "invite_users": "can_invite_users",
        "pin_messages": "can_pin_messages",
        "add_admins": "can_promote_members",
        "manage_call": "can_manage_video_chats",
        "anonymous": "is_anonymous",
    }
    if privilege not in privileges.keys():
        raise ValueError(f"{privilege} is not valid privileges")
    return privileges[privilege]


def parse_pre(text: str) -> typing.Tuple[str, typing.List[MessageEntityPre]]:
    text = text.strip()
    return (
        text,
        [MessageEntityPre(offset=0, length=len(add_surrogate(text)), language="")],
    )


def get_media_type(media: typing.Any) -> str:
    mdt = str((str(media)).split("(", maxsplit=1)[0])
    ret = ""
    if mdt == "MessageMediaDocument":
        mim = media.document.mime_type
        if mim == "application/x-tgsticker":
            ret = "sticker_anim"
        elif "image" in mim:
            if mim == "image/webp":
                ret = "sticker"
            elif mim == "image/gif":
                ret = "gif_doc"
            else:
                ret = "pic_doc"
        elif "video" in mim:
            if "DocumentAttributeAnimated" in str(media):
                ret = "gif"
            elif "DocumentAttributeVideo" in str(media):
                if "supports_streaming=True" in str(media.document.attributes[0]):
                    ret = "video"
                ret = "video_doc"
            else:
                ret = "video"
        elif "audio" in mim:
            ret = "audio"
        else:
            if mim.startswith(("text", "application")):
                ret = "text"
            else:
                ret = "document"
    elif mdt == "MessageMediaPhoto":
        ret = "pic"
    elif mdt == "MessageMediaWebPage":
        ret = "web"
    return ret
