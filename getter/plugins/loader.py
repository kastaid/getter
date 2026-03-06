# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from pathlib import Path
from random import choice

import aiofiles.os
from telethon.utils import get_extension

from . import (
    Root,
    get_media_type,
    kasta_cmd,
    plugins_help,
)

PLUGINS_DIR = Root / "getter/plugins"
CUSTOM_DIR = PLUGINS_DIR / "custom"


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
    if not reply or not reply.media:
        return await kst.eor("`Reply to a .py plugin file.`")
    mt = get_media_type(reply.media)
    yy = await kst.eor("`Processing...`")
    if mt == "text" and get_extension(reply.media) == ".py":
        plugin_file = "".join(_.file_name for _ in reply.media.document.attributes)
        plugin = Path(plugin_file).stem
        plugin_path = CUSTOM_DIR / plugin_file
        if plugin in ga._plugins:
            try:
                ga.unload_plugin(plugin)
                ga.log.info(f"Unloaded plugin {plugin}.")
            except Exception as err:
                ga.log.warning(f"Unload failed {plugin}: {err}")
                return await yy.eor(f"`Failed to unload plugin {plugin}.`")
        if await aiofiles.os.path.isfile(plugin_path):
            try:
                await aiofiles.os.remove(plugin_path)
            except Exception as err:
                ga.log.warning(f"Remove failed {plugin}: {err}")
        file = await reply.download_media(file=str(CUSTOM_DIR))
        if not file:
            return await yy.eor(f"`Failed to download plugin {plugin}.`")
        if ga.load_plugin(plugin_file):
            ga.log.success(f"Loaded plugin {plugin}.")
            await yy.eor(f"`Loaded plugin {plugin}.`")
        else:
            ga.log.warning(f"Load failed {plugin}.")
            await yy.eor(f"`Failed to load plugin {plugin}.`")
    else:
        await yy.eor("`Invalid plugin file.`")


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
        return await kst.eor("`Input plugin name.`")
    plugin = Path(plugin).stem
    yy = await kst.eor("`Processing...`")
    custom_path = CUSTOM_DIR / f"{plugin}.py"
    builtin_path = PLUGINS_DIR / f"{plugin}.py"
    if await aiofiles.os.path.isfile(custom_path) and plugin != "__init__":
        try:
            if plugin in ga._plugins:
                ga.unload_plugin(plugin)
            await aiofiles.os.remove(custom_path)
            ga.log.success(f"Unloaded plugin {plugin}.")
            await yy.eor(f"`Unloaded plugin {plugin}.`")
        except Exception as err:
            ga.log.warning(f"Unload failed {plugin}: {err}")
            await yy.eor(f"`Failed to unload plugin {plugin}.`")
    elif await aiofiles.os.path.isfile(builtin_path):
        await yy.eor("`Built-in plugins cannot be unloaded.`")
    else:
        await yy.eor(f"`Plugin {plugin} not found.`")


plugins_help["loader"] = {
    "{i}load [reply]": "Download/redownload and load a plugin.",
    "{i}unload [plugin_name]": "Unload and remove a plugin.",
}
