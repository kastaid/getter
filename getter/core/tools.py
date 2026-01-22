# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import subprocess
import sys
from functools import partial
from io import BytesIO
from re import sub
from typing import Any

import aiofiles.os
import aiohttp
import telegraph.aio

from getter import EXECUTOR, LOOP, __version__
from getter.logger import LOG

from .db import gvar, sgvar
from .utils import get_random_hex

_TGH: list[telegraph.aio.Telegraph] = []


def is_termux() -> bool:
    return "/com.termux" in sys.executable


async def aioify(func, *args, **kwargs):
    return await LOOP.run_in_executor(executor=EXECUTOR, func=partial(func, *args, **kwargs))


def import_lib(
    lib_name: str,
    pkg_name: str | None = None,
) -> Any:
    from importlib import import_module

    if pkg_name is None:
        pkg_name = lib_name
    lib_name = sub(r"(=|>|<|~).*", "", lib_name)
    try:
        return import_module(lib_name)
    except ImportError:
        done = subprocess.run(["python3", "-m", "pip", "install", "-U", pkg_name])
        if done.returncode != 0:
            raise AssertionError(f"Failed to install library {pkg_name} (pip exited with code {done.returncode})")
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
    post: bool | None = None,
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
            "User-Agent": "Python/{0[0]}.{0[1]} aiohttp/{1} getter/{2}".format(  # noqa: UP032
                sys.version_info,
                aiohttp.__version__,
                __version__,
            )
        }
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            if post:
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
            return None
        if resp.status not in {*{200, 201}, *statuses}:
            return None
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
        return None
    file_name = f"{file_name}_{get_random_hex()}.jpg"
    if not download:
        file = BytesIO(res)
        file.name = file_name
    else:
        file = "downloads/" + file_name
        async with aiofiles.open(file, mode="wb") as f:
            await f.write(res)
    return file


async def Screenshot(
    video: str,
    duration: int,
    output: str = "",
) -> str | None:
    ttl = duration // 2
    cmd = f"ffmpeg -v quiet -ss {ttl} -i {video} -vframes 1 {output}"
    await Runner(cmd)
    return output if await aiofiles.os.path.isfile(output) else None


async def MyIp() -> str:
    ips = (
        "https://ipinfo.io/ip",
        "https://ip.seeip.org",
        "http://ip-api.com/line/?fields=query",
        "https://checkip.amazonaws.com",
        "https://api.ipify.org",
        "https://ipaddr.site",
        "https://icanhazip.com",
        "https://ident.me",
        "https://curlmyip.net",
        "https://ipecho.net/plain",
    )
    statuses = {
        405,  # api.ipify.org
    }
    for url in ips:
        res = await Fetch(url, re_content=True, statuses=statuses)
        if res:
            return res.decode("utf-8").strip()
        continue
    return "null"


def Pinger(addr: str) -> str:
    try:
        import icmplib
    except ImportError:
        icmplib = import_lib(
            lib_name="icmplib",
            pkg_name="icmplib==3.0.3",
        )
    try:
        res = icmplib.ping(
            addr,
            count=1,
            interval=0.1,
            timeout=2,
            privileged=False,
        )
        return f"{res.avg_rtt}ms"
    except BaseException:
        try:
            out = subprocess.check_output(["ping", "-c", "1", addr]).decode()
            out = out.split("\n")
            rtt_line = ""
            for _ in out:
                if "min/avg/max" in _:
                    rtt_line = _
                    break
            rtt_line = rtt_line.replace(" ", "")
            rtt_line = rtt_line.split("=")[-1]
            rtt_line = rtt_line.split("/")[0]
            return f"{rtt_line}ms"
        except Exception as err:
            LOG.warning(err)
    return "--ms"


async def Telegraph(
    author: str | None = None,
) -> telegraph.aio.Telegraph:
    if _TGH:
        return next(reversed(_TGH), None)
    token = await gvar("_TELEGRAPH_TOKEN")
    api = telegraph.aio.Telegraph(token)
    if token:
        _TGH.append(api)
        return api
    if author is None:
        return api
    try:
        await api.create_account(
            short_name="getteruser",
            author_name=author[:128],
            author_url="https://t.me/kastaid",
        )
    except BaseException:
        return None
    await sgvar("_TELEGRAPH_TOKEN", api.get_access_token())
    _TGH.append(api)
    return api
