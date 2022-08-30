# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import time
from . import (
    __version__,
    __tlversion__,
    __layer__,
    __pyversion__,
    StartTime,
    hl,
    kasta_cmd,
    plugins_help,
    time_formatter,
    chunk,
    Hk,
)

help_text = """
█▀▀ █▀▀ ▀█▀ ▀█▀ █▀▀ █▀█
█▄█ ██▄ ░█░ ░█░ ██▄ █▀▄
┏━━━━━━━━━━━━━━━━━━━━━━━━
┣  <b>User</b> – <code>{}</code>
┣  <b>ID</b> – <code>{}</code>
┣  <b>Heroku App</b> – <code>{}</code>
┣  <b>Heroku Stack</b> – <code>{}</code>
┣  <b>Getter Version</b> – <code>{}</code>
┣  <b>Python Version</b> – <code>{}</code>
┣  <b>Telethon Version</b> – <code>{}</code>
┣  <b>Telegram Layer</b> – <code>{}</code>
┣  <b>Uptime</b> – <code>{}</code>
┣  <b>Handler</b> – <code>{}</code>
┣  <b>Plugins</b> – <code>{}</code>
┣  <b>Commands</b> – <code>{}</code>
┣  <b>Usage</b> – <code>{}help &lt;plugin name&gt;</code>
┗━━━━━━━━━━━━━━━━━━━━━━━━
<b>~ All plugins and their commands:</b>
{}

<b>Example:</b> Type <pre>{}help text</pre> for usage.

(c) @kastaid
"""


@kasta_cmd(
    pattern="help(?: |$)(.*)",
    edited=True,
    no_crash=True,
)
async def _(kst):
    arg = str((await kst.get_reply_message()).text if kst.is_reply else kst.pattern_match.group(1)).lower()
    yy = await kst.eor("`Loading...`")
    if arg:
        if arg in plugins_help:
            cmds = plugins_help[arg]
            text = f"**{len(cmds)} ==Help For {arg.upper()}==**  <`{hl}help {arg}`>\n\n"
            for cmd, desc in cmds.items():
                # cmd --> cmd.split(maxsplit=1)[0]
                # args --> cmd.split(maxsplit=1)cmd[1]
                text += "**❯** `{}`\n{}\n\n".format(cmd.replace("{i}", hl), desc.replace("{i}", hl))
            text += "(c) @kastaid"
            await yy.sod(text)
            return
        await yy.sod(f"**Invalid Plugin ➞** `{arg}`\nType ```{hl}help``` to see valid plugin names.")
        return
    plugins = ""
    for plug in chunk(sorted(plugins_help.keys()), 3):
        pr = ""
        for x in plug:
            pr += f"<code>{x}</code>  •  "
        pr = pr[:-3]
        plugins += f"\n{pr}"
    uptime = time_formatter((time.time() - StartTime) * 1000)
    text = help_text.format(
        kst.client.full_name,
        kst.client.uid,
        Hk.name or "none",
        Hk.stack,
        __version__,
        __pyversion__,
        __tlversion__,
        __layer__,
        uptime,
        hl,
        len(plugins_help),
        sum(len(v) for v in plugins_help.values()),
        hl,
        plugins,
        hl,
    )
    await yy.sod(text, parse_mode="html")


plugins_help["help"] = {
    "{i}help [plugin_name/reply]": "Get common/plugin/command help.",
}
