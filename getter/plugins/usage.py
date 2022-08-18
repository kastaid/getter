# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import datetime
import html
import json
import math
import shutil
import time
from . import (
    choice,
    StartTime,
    Var,
    HELP,
    kasta_cmd,
    humanbytes,
    time_formatter,
    todict,
    mask_email,
    USERAGENTS,
    Searcher,
    Heroku,
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
"""


def default_usage() -> str:
    import psutil

    app_uptime = time_formatter((time.time() - StartTime) * 1000)
    system_uptime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y %H:%M:%S")
    total, used, free = shutil.disk_usage(".")
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
    RAM = "{}%".format(psutil.virtual_memory().percent)
    DISK = "{}%".format(psutil.disk_usage("/").percent)
    UPLOAD = humanbytes(psutil.net_io_counters().bytes_sent)
    DOWN = humanbytes(psutil.net_io_counters().bytes_recv)
    TOTAL = humanbytes(total)
    USED = humanbytes(used)
    FREE = humanbytes(free)
    return usage_text.format(
        app_uptime,
        system_uptime,
        UPLOAD,
        DOWN,
        TOTAL,
        USED,
        FREE,
        CPU,
        RAM,
        DISK,
    )


async def heroku_usage() -> str:
    try:
        user_id = Heroku().account().id
        app = Heroku().app(Var.HEROKU_APP_NAME)
    except Exception as err:
        return f"<b>ERROR:</b>\n<code>{err}</code>"
    headers = {
        "User-Agent": choice(USERAGENTS),
        "Authorization": f"Bearer {Var.HEROKU_API}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    url = f"https://api.heroku.com/accounts/{user_id}/actions/get-quota"
    res = await Searcher(url, headers=headers, re_json=True)
    if not res:
        return "<code>Try again now!</code>"
    quota = res["account_quota"]
    quota_used = res["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    Apps = res["apps"]
    try:
        Apps[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = Apps[0]["quota_used"] / 60
        AppPercentage = math.floor(Apps[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    return dyno_text.format(
        app.name,
        app.stack.name,
        app.region.name,
        app.created_at.strftime("%d/%m/%Y %H:%M:%S"),
        app.updated_at.strftime("%d/%m/%Y %H:%M:%S"),
        mask_email(app.owner.email),
        AppHours,
        AppMinutes,
        AppPercentage,
        hours,
        minutes,
        percentage,
    )


@kasta_cmd(
    pattern="usage$",
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if Var.HEROKU_API and Var.HEROKU_APP_NAME:
        usage = default_usage() + await heroku_usage()
    else:
        usage = default_usage()
    await msg.eor(usage, parse_mode="html")


@kasta_cmd(
    pattern="heroku$",
)
async def _(kst):
    msg = await kst.eor("`Processing...`")
    if not Var.HEROKU_API:
        await msg.eor("Please set `HEROKU_API` in Config Vars.")
        return
    if not Var.HEROKU_APP_NAME:
        await msg.eor("Please set `HEROKU_APP_NAME` in Config Vars.")
        return
    try:
        heroku_conn = Heroku()
        app = heroku_conn.app(Var.HEROKU_APP_NAME)
    except Exception as err:
        return await msg.eor(f"**ERROR:**\n`{err}`")
    uid = kst.sender_id
    account = json.dumps(todict(heroku_conn.account()), indent=2, default=str)
    capp = json.dumps(todict(app.info), indent=2, default=str)
    dyno = json.dumps(todict(app.dynos()), indent=2, default=str)
    addons = json.dumps(todict(app.addons()), indent=2, default=str)
    buildpacks = json.dumps(todict(app.buildpacks()), indent=2, default=str)
    configs = json.dumps(app.config().to_dict(), indent=2, default=str)
    await kst.client.send_message(uid, f"<b>Account:</b>\n<pre>{html.escape(account)}</pre>", parse_mode="html")
    await asyncio.sleep(1)
    await kst.client.send_message(uid, f"<b>App:</b>\n<pre>{html.escape(capp)}</pre>", parse_mode="html")
    await asyncio.sleep(1)
    await kst.client.send_message(uid, f"<b>Dyno:</b>\n<pre>{html.escape(dyno)}</pre>", parse_mode="html")
    await asyncio.sleep(1)
    await kst.client.send_message(uid, f"<b>Addons:</b>\n<pre>{html.escape(addons)}</pre>", parse_mode="html")
    await asyncio.sleep(1)
    await kst.client.send_message(uid, f"<b>Buildpacks:</b>\n<pre>{html.escape(buildpacks)}</pre>", parse_mode="html")
    await asyncio.sleep(1)
    await kst.client.send_message(uid, f"<b>Configs:</b>\n<pre>{html.escape(configs)}</pre>", parse_mode="html")
    await msg.eor("`Sent at Saved Messages.`", time=5)


HELP.update(
    {
        "usage": [
            "Usage",
            """❯ `{i}usage`
Get overall usage, also heroku stats.

❯ `{i}heroku`
Get the heroku information (account, app, dyno, addons, buildpacks, configs) and save in Saved Messages.
""",
        ]
    }
)
