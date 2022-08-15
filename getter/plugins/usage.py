# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import datetime
import math
import shutil
import time
from . import (
    choice,
    StartTime,
    Var,
    HELP,
    humanbytes,
    kasta_cmd,
    time_formatter,
    Searcher,
    Heroku,
    HerokuStack,
)

dyno_text = """
**⚙️  Dyno Usage**
 -> **Dyno usage for** `{}` ~ {}:
     •  `{}h  {}m  {}%`
 -> **Dyno hours quota remaining this month:**
     •  `{}h  {}m  {}%`
"""

usage_text = """
**🖥️  Uptime**
**App:** `{}`
**System:** `{}`

**💾  Disk Space**
**Total:** `{}`
**Used:** `{}`
**Free:** `{}`

**📊  Data Usage**
**Upload:** `{}`
**Download:** `{}`

**📈  Memory Usage**
**CPU:** `{}`
**RAM:** `{}`
**DISK:** `{}`
"""

USERAGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) "
    "Chrome/19.0.1084.46 Safari/536.5",
    "Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) " "Chrome/19.0.1084.46 Safari/536.5",
]


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
    usage = usage_text.format(
        app_uptime,
        system_uptime,
        TOTAL,
        USED,
        FREE,
        UPLOAD,
        DOWN,
        CPU,
        RAM,
        DISK,
    )
    return usage


async def heroku_usage() -> str:
    if not Var.HEROKU_API:
        return "Please set `HEROKU_API` in Config Vars."
    if not Var.HEROKU_APP_NAME:
        return "Please set `HEROKU_APP_NAME` in Config Vars."
    try:
        heroku_conn = Heroku()
        user_id = heroku_conn.account().id
    except Exception as err:
        return f"**ERROR:**\n`{err}`"
    headers = {
        "User-Agent": choice(USERAGENTS),
        "Authorization": f"Bearer {Var.HEROKU_API}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    url = f"https://api.heroku.com/accounts/{user_id}/actions/get-quota"
    res = await Searcher(url, headers=headers, re_json=True)
    if not res:
        return "`Try again now!`"
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
    usage = default_usage() + dyno_text.format(
        Var.HEROKU_APP_NAME,
        HerokuStack(),
        AppHours,
        AppMinutes,
        AppPercentage,
        hours,
        minutes,
        percentage,
    )
    return usage


@kasta_cmd(
    pattern="usage(?: |$)(.*)",
)
async def _(kst):
    mode = kst.pattern_match.group(1)
    msg = await kst.eor("`Processing...`")
    if mode in ("heroku", "hk", "h"):
        hk = await heroku_usage()
        await msg.eor(hk)
    else:
        await msg.eor(default_usage())


HELP.update(
    {
        "usage": [
            "Usage",
            """❯ `{i}usage`
Get overall usage.

❯ `{i}usage <heroku|hk|h>`
Get heroku stats.
""",
        ]
    }
)
