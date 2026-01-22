# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import re
from functools import partial
from textwrap import shorten

from telethon import hints
from telethon.helpers import add_surrogate
from telethon.tl import functions as fun, types as typ
from telethon.utils import get_display_name

TELEGRAM_LINK_RE = r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog|space)/)([\w-]+)$"
USERNAME_RE = r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog|space)?(?:/)?(.*?))"
MSG_ID_RE = r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog|space)/)(?:c\/|)(.*)\/(.*)|(?:tg//openmessage\?)?(?:user_id=(.*))?(?:\&message_id=(.*))"


def is_telegram_link(url: str) -> bool:
    # TODO: support for username.t.me
    return bool(re.match(TELEGRAM_LINK_RE, url, flags=re.IGNORECASE))


def get_username(url: str) -> str:
    # TODO: support for username.t.me
    return "".join(re.sub(USERNAME_RE, "@", url, flags=re.IGNORECASE).split("/")[:1])


def get_msg_id(link: str) -> tuple[str | None, int | None]:
    # TODO: support for username.t.me
    idx = [tuple(filter(None, _)) for _ in re.findall(MSG_ID_RE, link, flags=re.IGNORECASE)]
    ids = next((_ for _ in idx), None)
    if not ids:
        return None, None
    chat, msg_id = ids
    if chat.isdecimal():
        chat = int("-100" + chat)
    return chat, int(msg_id)


def mentionuser(
    user_id: int | str,
    name: str,
    sep: str = "",
    width: int = 20,
    html: bool = False,
) -> str:
    name = shorten(name, width=width, placeholder="...")
    if name == "ㅤ":
        name = "?"
    return f"<a href=tg://user?id={user_id}>{sep}{name}</a>" if html else f"[{sep}{name}](tg://user?id={user_id})"


def display_name(entity: hints.Entity) -> str:
    name = get_display_name(entity)
    return name or "{}".format(getattr(entity, "first_name", "unknown") or "unknown")


def normalize_chat_id(chat_id: int | str) -> int | str:
    if str(chat_id).startswith(("-100", "-")) and str(chat_id)[1:].isdecimal():
        chat_id = int(str(chat_id).replace("-100", "").replace("-", ""))
    elif str(chat_id).isdecimal():
        chat_id = int(chat_id)
    return chat_id


async def get_chat_id(
    message: typ.Message,
    group: int = 1,
) -> int | str | None:
    chat_id = None
    target = await get_text(message, group=group)
    if not target:
        return int(str(message.chat_id).replace("-100", "").replace("-", ""))
    target = target.split(" ")[0]
    chat_id = normalize_chat_id(target)
    if isinstance(chat_id, str):
        if is_telegram_link(chat_id):
            chat_id = get_username(chat_id)
        try:
            full = await message.client(fun.messages.GetFullChatRequest(chat_id))
            chat_id = full.full_chat.id
        except BaseException:
            try:
                full = await message.client(fun.channels.GetFullChannelRequest(chat_id))
                chat_id = full.full_chat.id
            except BaseException:
                return None
    return chat_id


async def get_text(
    message: typ.Message,
    group: int = 1,
    plain: bool = True,
    strip: bool = True,
) -> str:
    match = message.pattern_match.group(group)
    if message.is_reply:
        reply = await message.get_reply_message()
        if not match:
            text = str(reply.message if plain else reply.text)
            if strip:
                text = text.strip()
            return text
    if strip:
        match = match.strip()
    return match


def get_user_status(user: typ.User) -> str:
    if user.bot or user.support:
        return "none"
    if isinstance(user.status, typ.UserStatusOnline):
        return "online"
    if isinstance(user.status, typ.UserStatusOffline):
        return "offline"
    if isinstance(user.status, typ.UserStatusRecently):
        return "recently"
    if isinstance(user.status, typ.UserStatusLastWeek):
        return "within_week"
    if isinstance(user.status, typ.UserStatusLastMonth):
        return "within_month"
    return "long_time_ago"


async def get_user(
    message: typ.Message,
    group: int = 1,
) -> tuple[typ.User | None, str | None]:
    args = message.pattern_match.group(group).strip().split(" ", 1)
    extra = ""
    try:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
                user = int(user)
            if message.message.entities:
                mention = message.message.entities[0]
                if isinstance(mention, typ.MessageEntityMentionName):
                    user_id = mention.user_id
                    user_obj = await message.client.get_entity(typ.PeerUser(user_id))
                    return user_obj, extra
            if isinstance(user, int) or user.startswith("@") or len(user) >= 5:
                user_obj = await message.client.get_entity(typ.PeerUser(user))
                return user_obj, extra
    except ValueError:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isdecimal() or (user.startswith("-") and user[1:].isdecimal()):
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
    except BaseException:
        pass
    try:
        extra = message.pattern_match.group(group).strip()
        if message.is_private:
            user_obj = await message.get_chat()
            return user_obj, extra
        if message.is_reply:
            reply = await message.get_reply_message()
            if reply.from_id is None:
                return None, None
            user_id = reply.sender_id
            try:
                user_obj = await message.client.get_entity(typ.PeerUser(user_id))
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
    except BaseException:
        pass
    return None, None


async def is_admin(
    message: typ.Message,
    chat_id: hints.EntityLike,
    user_id: hints.EntityLike,
) -> bool:
    try:
        prm = await message.client.get_permissions(chat_id, user_id)
        return bool(prm.is_admin)
    except BaseException:
        return False


async def admin_check(
    message: typ.Message,
    chat_id: hints.EntityLike,
    user_id: hints.EntityLike,
    require: str | None = None,
) -> bool:
    if message.is_private:
        return True
    try:
        prm = await message.client.get_permissions(chat_id, user_id)
    except BaseException:
        return False
    if not prm.is_admin:
        return False
    return not (require and not getattr(prm, require, False))


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
    if privilege not in privileges:
        raise ValueError(f"{privilege} is not valid privileges")
    return privileges[privilege]


def parse_pre(text: str) -> tuple[str, list[typ.MessageEntityPre]]:
    text = text.strip()
    return (
        text,
        [typ.MessageEntityPre(offset=0, length=len(add_surrogate(text)), language="")],
    )


def get_media_type(media: typ.TypeMessageMedia) -> str:
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
            ret = "text" if mim.startswith(("text", "application")) else "document"
    elif mdt == "MessageMediaPhoto":
        ret = "pic"
    elif mdt == "MessageMediaWebPage":
        ret = "web"
    return ret
