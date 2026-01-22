# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from datetime import datetime
from html import escape
from random import choice

from telethon import events

from . import (
    DEFAULT_GUCAST_BLACKLIST,
    DEVS,
    NOCHATS,
    OUTS_AFK,
    add_afk,
    del_afk,
    get_blacklisted,
    getter_app,
    gvar,
    is_afk,
    is_allow,
    kasta_cmd,
    plugins_help,
    set_last_afk,
    time_formatter,
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
    pattern=r"afk(?: |$)([\s\S]*)",
)
@kasta_cmd(
    pattern=r"brb(?: |$)([\s\S]*)",
    no_handler=True,
)
async def _(kst):
    if await is_afk():
        return
    yy = await kst.eor("`Go To AFK...`")
    start = datetime.now().timestamp()
    reason = await kst.client.get_text(kst, plain=False)
    text = "<b><u>I`m now AFK ツ</u></b>"
    if reason:
        reason = escape(reason)
        text += f"\n<b>Reason:</b> <pre>{reason}</pre>"
    await add_afk(reason, start)
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
    afk = await is_afk()
    if afk:
        start = datetime.fromtimestamp(afk.start)
        end = datetime.now().replace(microsecond=0)
        afk_time = time_formatter((end - start).seconds * 1000)
        try:
            for x, y in afk.last.items():
                await kst.client.delete_messages(int(x), [y])
        except BaseException:
            pass
        await del_afk()
        myself = escape(kst.client.full_name)
        text = f"{myself}\n"
        text += f"{choice(OUTS_AFK)}\n"
        text += f"<i>Was away for</i> – {afk_time}"
        await kst.eod(text, parse_mode="html")


async def OnAFK(kst):
    if any(_ in kst.raw_text.lower() for _ in ("afk", "brb")):
        return
    if not await is_afk():
        return
    user = await kst.get_sender()
    if getattr(user, "bot", False) or getattr(user, "support", False) or getattr(user, "verified", False):
        return
    if kst.chat_id in NOCHATS and user.id not in DEVS:
        return
    if kst.is_private and await gvar("_pmguard", use_cache=True) and not await is_allow(user.id, use_cache=True):
        return
    GUCAST_BLACKLIST = await get_blacklisted(
        url="https://raw.githubusercontent.com/kastaid/resources/main/gucastblacklist.py",
        attempts=1,
        fallbacks=DEFAULT_GUCAST_BLACKLIST,
    )
    if user.id in {*DEVS, *GUCAST_BLACKLIST}:
        return
    afk = await is_afk()
    if afk:
        start = datetime.fromtimestamp(afk.start)
        end = datetime.now().replace(microsecond=0)
        afk_time = time_formatter((end - start).seconds * 1000)
        text = "<b><u>I`m on AFK ツ</u></b>\n"
        text += f"Last seen {afk_time} ago."
        reason = f"<pre>{afk.reason}</pre>" if afk.reason else "No reason."
        text += f"\n<b>Reason:</b> {reason}"
        chat_id = str(kst.chat_id)
        if chat_id in afk.last:
            try:
                await kst.client.delete_messages(int(chat_id), [afk.last[chat_id]])
            except BaseException:
                pass
        last = await kst.reply(
            text,
            link_preview=False,
            parse_mode="html",
        )
        await set_last_afk(chat_id, last.id)


async def handle_afk() -> None:
    if await is_afk():
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
