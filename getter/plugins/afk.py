# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import datetime
import html
from . import (
    DEVS,
    NOCHATS,
    getter_app,
    kasta_cmd,
    plugins_help,
    DEFAULT_GUCAST_BLACKLIST,
    get_blacklisted,
    events,
    choice,
    suppress,
    time_formatter,
    OUTS_AFK,
    is_afk,
    add_afk,
    del_afk,
    set_last_afk,
    gvar,
    is_allow,
)

_ON_STOP = (
    "afk",
    "brb",
    "getter",
    "#anti_pm",
    "#blocked",
    "#archived",
    "#new_message",
    "#gbanned_watch",
    "#gmuted_watch",
)


@kasta_cmd(
    pattern="afk(?: |$)((?s).*)",
)
@kasta_cmd(
    pattern="brb(?: |$)((?s).*)",
    no_handler=True,
)
async def _(kst):
    if is_afk():
        return
    yy = await kst.eor("`Go To AFK...!!`")
    start = datetime.datetime.now().timestamp()
    reason = await kst.client.get_text(kst, plain=False)
    text = "<b><u>I`m Going AFK ツ</u></b>"
    if reason:
        reason = html.escape(reason)
        text += f"\n<b>Reason:</b> <pre>{reason}</pre>"
    add_afk(reason, start)
    getter_app.add_handler(
        StopAFK,
        event=events.NewMessage(
            outgoing=True,
            forwards=False,
        ),
    )
    getter_app.add_handler(
        OnAFK,
        event=events.NewMessage(
            incoming=True,
            func=lambda e: bool(e.mentioned or e.is_private),
            forwards=False,
        ),
    )
    await yy.eod(text, parse_mode="html")


async def StopAFK(kst):
    if any(_ in kst.raw_text.lower() for _ in _ON_STOP):
        return
    if kst.chat_id in NOCHATS and kst.client.uid not in DEVS:
        return
    if is_afk():
        start = datetime.datetime.fromtimestamp(is_afk().start)
        end = datetime.datetime.now().replace(microsecond=0)
        afk_time = time_formatter((end - start).seconds * 1000)
        with suppress(BaseException):
            for x, y in is_afk().last.items():
                await kst.client.delete_messages(int(x), [y])
        del_afk()
        myself = html.escape(kst.client.full_name)
        text = f"{myself}\n"
        text += f"{choice(OUTS_AFK)}\n"
        text += f"<i>Was away for</i> ~ {afk_time}"
        await kst.respond(
            text,
            link_preview=False,
            parse_mode="html",
        )


async def OnAFK(kst):
    if any(_ in kst.raw_text.lower() for _ in ("afk", "brb")):
        return
    if not is_afk():
        return
    user = await kst.get_sender()
    if getattr(user, "bot", False) or getattr(user, "support", False) or getattr(user, "verified", False):
        return
    if kst.chat_id in NOCHATS and user.id not in DEVS:
        return
    if kst.is_private and gvar("_pmguard", use_cache=True) and not is_allow(user.id, use_cache=True):
        return
    GUCAST_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/gucastblacklist.py",
        attempts=1,
        fallbacks=DEFAULT_GUCAST_BLACKLIST,
    )
    if user.id in {*DEVS, *GUCAST_BLACKLIST}:
        return
    if is_afk():
        start = datetime.datetime.fromtimestamp(is_afk().start)
        end = datetime.datetime.now().replace(microsecond=0)
        afk_time = time_formatter((end - start).seconds * 1000)
        text = "<b><u>I`m Now AFK ツ</u></b>\n"
        text += f"Last seen {afk_time} ago."
        reason = f"<pre>{is_afk().reason}</pre>" if is_afk().reason else "No reason."
        text += f"\n<b>Reason:</b> {reason}"
        chat_id = str(kst.chat_id)
        if chat_id in is_afk().last:
            with suppress(BaseException):
                await kst.client.delete_messages(int(chat_id), [is_afk().last[chat_id]])
        last = await kst.reply(
            text,
            link_preview=False,
            parse_mode="html",
        )
        set_last_afk(chat_id, last.id)


if is_afk():
    getter_app.add_handler(
        StopAFK,
        event=events.NewMessage(
            outgoing=True,
            forwards=False,
        ),
    )
    getter_app.add_handler(
        OnAFK,
        event=events.NewMessage(
            incoming=True,
            func=lambda e: bool(e.mentioned or e.is_private),
            forwards=False,
        ),
    )


plugins_help["afk"] = {
    "{i}afk [reason]/[reply]": "When you are in AFK if anyone tags you then will notify them if you're AFK unless if 'afk' or 'brb' words is exists!",
    "brb": """Alias for afk command, without handler!

**Note:**
- AFK is abbreviation for “Away From Keyboard”.
- BRB also abbreviation for “Be Right Back”.
- To stopping AFK just typing at anywhere.
- To continue AFK put the 'afk' or 'brb' word in message.
- AFK Ignored user that not allowed to PM at pmpermit.
- When AFK not stopped, this will continue even if the bot restarted.
""",
}
