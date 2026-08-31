# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import re
import subprocess
import sys
from importlib import import_module
from io import BytesIO
from pathlib import Path
from typing import Any

import aiohttp

from getter import DOWNLOAD_DIR, __version__

from .utils import get_random_hex

_LIB_NAME_RE = re.compile(r"[=><~].*")


def is_termux() -> bool:
    return "/com.termux" in sys.executable


def import_lib(
    lib_name: str,
    pkg_name: str | None = None,
) -> Any:
    if pkg_name is None:
        pkg_name = lib_name
    lib_name = _LIB_NAME_RE.sub("", lib_name)
    try:
        return import_module(lib_name)
    except ImportError as err:
        try:
            done = subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "-U",
                    pkg_name,
                ],
                check=False,
            )
        except FileNotFoundError:
            done = subprocess.run(
                [
                    "python3",
                    "-m",
                    "pip",
                    "install",
                    "--prefer-binary",
                    "-U",
                    pkg_name,
                ],
                check=False,
            )
        if done.returncode != 0:
            raise AssertionError(f"Failed to install {pkg_name} (code {done.returncode})") from err
        return import_module(lib_name)


async def Runner(cmd: str) -> tuple[str, str, int, int]:
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await proc.communicate()
    except BaseException:
        stdout, stderr = "", ""
    return (
        stdout.decode().strip(),
        stderr.decode().strip(),
        proc.returncode,
        proc.pid,
    )


async def Fetch(
    url: str,
    head: bool = False,
    post: bool = False,
    headers: dict | None = None,
    params: dict | None = None,
    json: dict | None = None,
    data: dict | None = None,
    ssl: Any = None,
    re_json: bool = False,
    re_content: bool = False,
    real: bool = False,
    statuses: set[int] | None = None,
    **args,
) -> Any:
    statuses = statuses or {}
    if not headers:
        headers = {
            "User-Agent": f"Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__} getter/{__version__}"
        }
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            if head:
                resp = await session.head(
                    url=url,
                    params=params,
                    ssl=ssl,
                    raise_for_status=False,
                    **args,
                )
            elif post:
                resp = await session.post(
                    url=url,
                    json=json,
                    data=data,
                    ssl=ssl,
                    raise_for_status=False,
                    **args,
                )
            else:
                resp = await session.get(
                    url=url,
                    params=params,
                    ssl=ssl,
                    raise_for_status=False,
                    **args,
                )
        except BaseException:
            return
        if resp.status not in {*{200, 201}, *statuses}:
            return
        if re_json:
            return await resp.json(content_type=None)
        if re_content:
            return await resp.read()
        if real:
            return resp
        return await resp.text()


async def Carbon(
    code: str,
    url: str = "carbon/api/cook",
    file_name: str = "carbon",
    download: bool = False,
    rayso: bool = False,
    **kwargs: Any | None,
) -> Any:
    kwargs["code"] = code
    if rayso:
        url = "rayso/api"
        kwargs["title"] = kwargs.get("title", "getter")
        kwargs["theme"] = kwargs.get("theme", "raindrop")
        kwargs["darkMode"] = kwargs.get("darkMode", True)
        kwargs["background"] = kwargs.get("background", True)
    res = await Fetch(
        url,
        post=True,
        json=kwargs,
        re_content=True,
    )
    if not res:
        return
    file_name = f"{file_name}_{get_random_hex()}.jpg"
    if not download:
        file = BytesIO(res)
        file.name = file_name
    else:
        file = DOWNLOAD_DIR / file_name
        await asyncio.to_thread(file.write_bytes, res)
    return file


async def Screenshot(
    video: str,
    duration: int,
    output: str = "",
) -> str | None:
    ttl = duration // 2
    cmd = f"ffmpeg -v quiet -ss {ttl} -i {video} -vframes 1 {output}"
    await Runner(cmd)
    return output if await asyncio.to_thread(Path(output).is_file) else None
