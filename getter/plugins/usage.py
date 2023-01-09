# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import json
from datetime import datetime
from html import escape
from math import floor
from . import (
    getter_app,
    kasta_cmd,
    plugins_help,
    choice,
    humanbytes,
    to_dict,
    formatx_send,
    mask_email,
    USERAGENTS,
    Fetch,
    hk,
    sendlog,
)

dyno_text = """
<b>📦 Heroku App</b>
-> <b>Name:</b> <code>{}</code>
-> <b>Stack:</b> <code>{}</code>
-> <b>Region:</b> <code>{}</code>
-> <b>Created:</b> <code>{}</code>
-> <b>Updated:</b> <code>{}</code>
-> <b>Email:</b> <code>{}</code>

<b>⚙️ Heroku Dyno</b>
-> <b>Dyno usage:</b>
    •  <code>{}h  {}m  {}%</code>
-> <b>Dyno hours quota remaining this month:</b>
    •  <code>{}h  {}m  {}%</code>
"""
usage_text = """
<b>🖥️ Uptime</b>
<b>App:</b> <code>{}</code>
<b>System:</b> <code>{}</code>

<b>📊 Data Usage</b>
<b>Upload:</b> <code>{}</code>
<b>Download:</b> <code>{}</code>

<b>💾 Disk Space</b>
<b>Total:</b> <code>{}</code>
<b>Used:</b> <code>{}</code>
<b>Free:</b> <code>{}</code>

<b>📈 Memory Usage</b>
<b>CPU:</b> <code>{}</code>
<b>RAM:</b> <code>{}</code>
<b>DISK:</b> <code>{}</code>
<b>SWAP:</b> <code>{}</code>
"""


@kasta_cmd(
    pattern="usage$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    if hk.is_heroku:
        usage = default_usage() + await heroku_usage()
    else:
        usage = default_usage()
    await yy.eor(usage, parse_mode="html")


@kasta_cmd(
    pattern="heroku$",
)
async def _(kst):
    yy = await kst.eor("`Processing...`")
    if not hk.api:
        await yy.eod("Please set `HEROKU_API` in Config Vars.")
        return
    if not hk.name:
        await yy.eod("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        conn = hk.heroku()
        app = conn.app(hk.name)
    except Exception as err:
        return await yy.eor(formatx_send(err), parse_mode="html")
    account = json.dumps(to_dict(conn.account()), indent=1, default=str)
    capp = json.dumps(to_dict(app.info), indent=1, default=str)
    dyno = json.dumps(to_dict(app.dynos()), indent=1, default=str)
    addons = json.dumps(to_dict(app.addons()), indent=1, default=str)
    buildpacks = json.dumps(to_dict(app.buildpacks()), indent=1, default=str)
    configs = json.dumps(app.config().to_dict(), indent=1, default=str)
    await sendlog(f"<b>Account:</b>\n<pre>{escape(account)}</pre>", fallback=True, parse_mode="html")
    await asyncio.sleep(1)
    await sendlog(f"<b>App:</b>\n<pre>{escape(capp)}</pre>", fallback=True, parse_mode="html")
    await asyncio.sleep(1)
    await sendlog(f"<b>Dyno:</b>\n<pre>{escape(dyno)}</pre>", fallback=True, parse_mode="html")
    await asyncio.sleep(1)
    await sendlog(f"<b>Addons:</b>\n<pre>{escape(addons)}</pre>", fallback=True, parse_mode="html")
    await asyncio.sleep(1)
    await sendlog(f"<b>Buildpacks:</b>\n<pre>{escape(buildpacks)}</pre>", fallback=True, parse_mode="html")
    await asyncio.sleep(1)
    await sendlog(f"<b>Configs:</b>\n<pre>{escape(configs)}</pre>", fallback=True, parse_mode="html")
    await yy.eor("`Heroku details sent at botlogs.`")


def default_usage() -> str:
    import psutil

    try:
        UPLOAD = humanbytes(psutil.net_io_counters().bytes_sent)
    except BaseException:
        UPLOAD = 0
    try:
        DOWN = humanbytes(psutil.net_io_counters().bytes_recv)
    except BaseException:
        DOWN = 0
    try:
        workdir = psutil.disk_usage(".")
        TOTAL = humanbytes(workdir.total)
        USED = humanbytes(workdir.used)
        FREE = humanbytes(workdir.free)
    except BaseException:
        TOTAL = 0
        USED = 0
        FREE = 0
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = "{}GHz".format(round(cpu_freq / 1000, 2))
        else:
            cpu_freq = "{}MHz".format(round(cpu_freq, 2))
        CPU = "{}% ({}) {}".format(psutil.cpu_percent(), psutil.cpu_count(), cpu_freq)
    except BaseException:
        try:
            CPU = "{}%".format(psutil.cpu_percent())
        except BaseException:
            CPU = "0%"
    try:
        RAM = "{}%".format(psutil.virtual_memory().percent)
    except BaseException:
        RAM = "0%"
    try:
        DISK = "{}%".format(psutil.disk_usage("/").percent)
    except BaseException:
        DISK = "0%"
    try:
        swap = psutil.swap_memory()
        SWAP = "{} | {}%".format(humanbytes(swap.total), swap.percent or 0)
    except BaseException:
        SWAP = "0 | 0%"
    return usage_text.format(
        getter_app.uptime,
        datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        UPLOAD,
        DOWN,
        TOTAL,
        USED,
        FREE,
        CPU,
        RAM,
        DISK,
        SWAP,
    )


async def heroku_usage() -> str:
    try:
        conn = hk.heroku()
        user = conn.account().id
        app = conn.app(hk.name)
    except Exception as err:
        return f"<b>ERROR:</b>\n<code>{err}</code>"
    headers = {
        "User-Agent": choice(USERAGENTS),
        "Authorization": f"Bearer {hk.api}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    url = f"https://api.heroku.com/accounts/{user}/actions/get-quota"
    res = await Fetch(url, headers=headers, re_json=True)
    if not res:
        return "<code>Try again now!</code>"
    quota = res["account_quota"]
    quota_used = res["quota_used"]
    remaining_quota = quota - quota_used
    percentage = floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = floor(minutes_remaining / 60)
    minutes = floor(minutes_remaining % 60)
    Apps = res["apps"]
    try:
        Apps[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = Apps[0]["quota_used"] / 60
        AppPercentage = floor(Apps[0]["quota_used"] * 100 / quota)
    AppHours = floor(AppQuotaUsed / 60)
    AppMinutes = floor(AppQuotaUsed % 60)
    return dyno_text.format(
        app.name,
        app.stack.name,
        app.region.name,
        app.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        app.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        mask_email(app.owner.email),
        AppHours,
        AppMinutes,
        AppPercentage,
        hours,
        minutes,
        percentage,
    )


plugins_help["usage"] = {
    "{i}usage": "Get overall usage, also heroku stats.",
    "{i}heroku": "Get the heroku information (account, app, dyno, addons, buildpacks, configs) and save in botlogs.",
}
