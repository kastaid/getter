# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from . import (
    __layer__,
    __pyversion__,
    __tlversion__,
    __version__,
    chunk,
    gvar,
    hl,
    humanbool,
    kasta_cmd,
    plugins_help,
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
<b>~ All plugins name and commands</b>:

{}

<blockquote><b>Usage</b>: <code>{}help [plugin_name]</code>
<b>Tips</b>:
- To check how fast response use <code>{}ping</code>
- Get details about ur self use <code>{}test</code>
- Collect ur stats by using <code>{}stats</code>
- Get users ids use <code>{}id</code>
- Get users info use <code>{}info</code></blockquote>
"""


@kasta_cmd(
    pattern="help(?: |$)(.*)",
    edited=True,
)
async def _(kst):
    ga = kst.client
    yy = await kst.eor("`Loading...`")
    plugin_name = (await ga.get_text(kst)).lower()
    if plugin_name:
        if plugin_name in plugins_help:
            name = plugin_name
        else:
            name = next((i for i in plugin_name.split() if i in plugins_help), None)
        if name:
            cmds = plugins_help[name]
            text = f"**{len(cmds)} Help for {name.upper()}**  <`{hl}help {name}`>\n\n"
            for cmd, desc in cmds.items():
                text += "**❯** `{}`\n{}\n\n".format(cmd.replace("{i}", hl), desc.strip().replace("{i}", hl))
            return await yy.sod(text)
        return await yy.sod(
            f"**404 Plugin Not Found  ➞**  `{plugin_name}`\nType  `{hl}help`  to see valid plugins name."
        )
    plugins = ""
    for plug in chunk(sorted(plugins_help), 3):
        pr = ""
        for _ in plug:
            pr += f"<code>{_}</code> • "
        pr = pr[:-3]
        plugins += f"\n{pr}"
    await yy.sod(
        help_text.format(
            ga.full_name,
            ga.uid,
            __version__,
            __pyversion__,
            __tlversion__,
            __layer__,
            ga.uptime,
            plugins_help.count,
            plugins_help.total,
            humanbool(await gvar("_sudo", use_cache=True), toggle=True),
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
