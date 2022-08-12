# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from platform import python_version
from time import time
from telethon.version import __version__ as telethonver
from . import (
    __version__ as getterver,
    __layer__,
    StartTime,
    HELP,
    hl,
    kasta_cmd,
    Var,
    display_name,
    time_formatter,
)

help_text = """
█▀▀ █▀▀ ▀█▀ ▀█▀ █▀▀ █▀█
█▄█ ██▄ ░█░ ░█░ ██▄ █▀▄
┏━━━━━━━━━━━━━━━━━━━━━━━━
┣  <b>User</b> – <code>{}</code>
┣  <b>ID</b> – <code>{}</code>
┣  <b>Heroku App</b> – <code>{}</code>
┣  <b>Getter Version</b> – <code>{}</code>
┣  <b>Python Version</b> – <code>{}</code>
┣  <b>Telethon Version</b> – <code>{} Layer: {}</code>
┣  <b>Uptime</b> – <code>{}</code>
┣  <b>Handler</b> – <code>{}</code>
┣  <b>Plugins</b> – <code>{}</code>
┣  <b>Usage</b> – <code>{}help &lt;plugin name&gt;</code>
┗━━━━━━━━━━━━━━━━━━━━━━━━
<b>~ All plugins and commands are below:</b>

{}

<b>Example:</b> Type <pre>{}help core</pre> for usage.
"""


@kasta_cmd(
    pattern="help(?: |$)(.*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    args = kst.pattern_match.group(1).lower()
    msg = await kst.eor("`Loading...`")
    if args:
        if args in HELP:
            _ = "**📦 Getter Plugin {}** <`{}help {}`>\n\n{}".format(
                HELP[args][0],
                hl,
                args,
                HELP[args][1].replace("{i}", hl),
            )
            await msg.eor(_)
        else:
            await msg.eor(f"**📦 Invalid Plugin ➞** `{args}`\nType ```{hl}help``` to see valid plugin names.")
    else:
        uptime = time_formatter((time() - StartTime) * 1000)
        plugins = ""
        for _ in HELP:
            plugins += f"<code>{_}</code>  ★  "
        plugins = plugins[:-3]
        me = await kst.client.get_me()
        text = help_text.format(
            display_name(me),
            kst.client.uid,
            Var.HEROKU_APP_NAME or "None",
            getterver,
            python_version(),
            telethonver,
            __layer__,
            uptime,
            hl,
            len(HELP),
            hl,
            plugins,
            hl,
        )
        await msg.eor(text, parse_mode="html")
