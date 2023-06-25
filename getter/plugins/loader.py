# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import os.path
from os import remove
from telethon.utils import get_extension
from . import kasta_cmd, plugins_help, get_media_type

base = os.path.dirname(os.path.realpath(__file__))


@kasta_cmd(
    pattern="load$",
)
async def _(kst):
    reply = await kst.get_reply_message()
    if not reply or reply and not reply.media:
        return await kst.eor("`Please reply a message contains file with plugin_name.py`")
    mt = get_media_type(reply.media)
    yy = await kst.eor("`Processing...`")
    if mt == "text" and get_extension(reply.media) == ".py":
        plugin = "".join([_.file_name for _ in reply.media.document.attributes]).replace(".py", "")
        if os.path.exists(f"{base}/custom/{plugin}.py"):
            remove(f"{base}/custom/{plugin}.py")
        file = await reply.download_media(file=f"{base}/custom")
        if file:
            done = await yy.eor(f"`The plugin {plugin} is loaded!`")
            msg = await done.reply("`Rebooting to apply...`", silent=True)
            await kst.client.reboot(msg)
        else:
            await yy.eor(f"`Failed to download the plugin {plugin}.`")
    else:
        await yy.eor("`Is not valid plugin.`")


@kasta_cmd(
    pattern="unload(?: |$)(.*)",
)
async def _(kst):
    plugin = await kst.client.get_text(kst, plain=True)
    if not plugin:
        return await kst.eor("`Please input plugin name.`")
    plugin = plugin.replace(".py", "")
    yy = await kst.eor("`Processing...`")
    if os.path.exists(f"{base}/custom/{plugin}.py") and plugin != "__init__":
        remove(f"{base}/custom/{plugin}.py")
        done = await yy.eor(f"`The plugin {plugin} removed!`")
        msg = await done.reply("`Rebooting to apply...`", silent=True)
        await kst.client.reboot(msg)
    elif os.path.exists(f"{base}/{plugin}.py"):
        await yy.eor("`It is forbidden to remove built-in plugins, it will disrupt the updater!`")
    else:
        await yy.eor(f"`Plugin {plugin} not found.`")


plugins_help["loader"] = {
    "{i}load [reply]": "Download/redownload and load the plugin.",
    "{i}unload [plugin_name]": "Delete plugin.",
}
