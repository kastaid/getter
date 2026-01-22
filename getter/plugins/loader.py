# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from os.path import dirname, realpath
from random import choice

import aiofiles.os
from telethon.utils import get_extension

from . import get_media_type, kasta_cmd, plugins_help

base = dirname(realpath(__file__))


@kasta_cmd(
    pattern="load$",
)
@kasta_cmd(
    pattern="gload$",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((2, 4)))
    ga = kst.client
    reply = await kst.get_reply_message()
    if not reply or (reply and not reply.media):
        return await kst.eor("`Please reply a message contains file with plugin_name.py`")
    mt = get_media_type(reply.media)
    yy = await kst.eor("`Processing...`")
    if mt == "text" and get_extension(reply.media) == ".py":
        plugin_file = "".join([_.file_name for _ in reply.media.document.attributes])
        plugin = plugin_file.replace(".py", "")
        if await aiofiles.os.path.isfile(f"{base}/custom/{plugin_file}"):
            if plugin in ga._plugins:
                ga.unload_plugin(plugin)
            try:
                await aiofiles.os.remove(f"{base}/custom/{plugin_file}")
            except BaseException:
                pass
        file = await reply.download_media(file=f"{base}/custom")
        if file:
            if ga.load_plugin(plugin_file):
                await yy.eor(f"`The plugin {plugin} is loaded.`")
            else:
                await yy.eor(f"`The plugin {plugin} is not loaded.`")
        else:
            await yy.eor(f"`Failed to download the plugin {plugin}.`")
    else:
        await yy.eor("`Is not valid plugin.`")


@kasta_cmd(
    pattern="unload(?: |$)(.*)",
)
@kasta_cmd(
    pattern="gunload(?: |$)(.*)",
    dev=True,
)
async def _(kst):
    if kst.is_dev:
        await asyncio.sleep(choice((2, 4)))
    ga = kst.client
    plugin = await ga.get_text(kst, plain=True)
    if not plugin:
        return await kst.eor("`Please input plugin name.`")
    plugin = plugin.replace(".py", "")
    yy = await kst.eor("`Processing...`")
    if await aiofiles.os.path.isfile(f"{base}/custom/{plugin}.py") and plugin != "__init__.py":
        try:
            if plugin in ga._plugins:
                ga.unload_plugin(plugin)
            await aiofiles.os.remove(f"{base}/custom/{plugin}.py")
            ga.log.success(f"Successfully to remove custom plugin {plugin}")
            await yy.eor(f"`The plugin {plugin} removed.`")
        except BaseException:
            ga.log.error(f"Failed to remove custom plugin {plugin}")
            await yy.eor(f"`The plugin {plugin} can't remove, please try again.`")
    elif await aiofiles.os.path.isfile(f"{base}/{plugin}.py"):
        await yy.eor("`It is forbidden to remove built-in plugins, it will disrupt the updater!`")
    else:
        await yy.eor(f"`Plugin {plugin} not found.`")


plugins_help["loader"] = {
    "{i}load [reply]": "Download/redownload and load the plugin.",
    "{i}unload [plugin_name]": "Delete plugin.",
}
