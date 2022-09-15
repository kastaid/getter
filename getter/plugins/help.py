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
    humanbool,
    gvar,
)

help_text = """
█▀▀ █▀▀ ▀█▀ ▀█▀ █▀▀ █▀█
█▄█ ██▄ ░█░ ░█░ ██▄ █▀▄
┏━━━━━━━━━━━━━━━━━━━━━━━━
┣  <b>User</b>  –  <code>{}</code>
┣  <b>ID</b>  –  <code>{}</code>
┣  <b>Getter Version</b>  –  <code>{}</code>
┣  <b>Python Version</b>  –  <code>{}</code>
┣  <b>Telethon Version</b>  –  <code>{}</code>
┣  <b>Telegram Layer</b>  –  <code>{}</code>
┣  <b>Uptime</b>  –  <code>{}</code>
┣  <b>Plugins</b>  –  <code>{}</code>
┣  <b>Commands</b>  –  <code>{}</code>
┣  <b>Sudo</b>  –  <code>{}</code>
┗━━━━━━━━━━━━━━━━━━━━━━━━
<b>~ All plugins names and commands:</b>

{}

<b>Usage:</b> <code>{}help [plugin_name]</code>
<b>Tips:</b>
- To check how fast response use <code>{}ping</code>
- Get details about ur self use <code>{}test</code>
- Collect ur stats by using <code>{}stats</code>
- Get users ids use <code>{}id</code>
- Get users info use <code>{}info</code>

(c) @kastaid #getter
"""


@kasta_cmd(
    pattern="help(?: |$)(.*)",
    edited=True,
)
async def _(kst):
    plugin_name = (await kst.client.get_text(kst)).lower()
    yy = await kst.eor("`Loading...`")
    if plugin_name:
        name = None
        if plugin_name in plugins_help:
            name = plugin_name
        else:
            for _ in plugin_name.split():
                if _ in plugins_help:
                    name = _
                    break
        if name:
            cmds = plugins_help[name]
            text = f"**{len(cmds)} ==Help For {name.upper()}==**  <`{hl}help {name}`>\n\n"
            for cmd, desc in cmds.items():
                # cmd --> cmd.split(maxsplit=1)[0]
                # args --> cmd.split(maxsplit=1)[1]
                text += "**❯** `{}`\n{}\n\n".format(cmd.replace("{i}", hl), desc.strip().replace("{i}", hl))
            text += "(c) @kastaid #getter"
            await yy.sod(text)
            return
        await yy.sod(f"**404 Plugin Not Found  ➞**  `{plugin_name}`\nType  `{hl}help`  to see valid plugins name.")
        return
    plugins = ""
    for plug in chunk(sorted(plugins_help), 3):
        _pr = ""
        for _ in plug:
            _pr += f"<code>{_}</code> • "
        _pr = _pr[:-3]
        plugins += f"\n{_pr}"
    uptime = time_formatter((time.time() - StartTime) * 1000)
    await yy.sod(
        help_text.format(
            kst.client.full_name,
            kst.client.uid,
            __version__,
            __pyversion__,
            __tlversion__,
            __layer__,
            uptime,
            plugins_help.count,
            plugins_help.total,
            humanbool(gvar("_sudo", use_cache=True), toggle=True),
            plugins.strip(),
            hl,
            hl,
            hl,
            hl,
            hl,
            hl,
        ),
        parse_mode="html",
    )


plugins_help["help"] = {
    "{i}help [plugin_name]/[reply]": "Get common/plugin/command help by filling the plugin name or reply single word or message that contains plugin name.",
}
