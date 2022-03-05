# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import shutil as shu
from contextlib import suppress
from datetime import datetime
from math import floor
from secrets import choice
from time import time
import psutil as psu
from heroku3 import from_key
from . import (
    StartTime,
    Var,
    HELP,
    humanbytes,
    kasta_cmd,
    time_formatter,
    Searcher,
)

usage = """
**🖥️ Uptime 🖥️**
**App:** `{}`
**System:** `{}`

**⚙️ Dyno Usage ⚙️**
-> **Dyno usage for** `{}`:
  •  `{}h`  `{}m`  [`{}%`]
-> **Dyno hours quota remaining this month:**
  •  `{}h`  `{}m`  [`{}%`]

**💾 Disk Space 💾**
**Total:** `{}`
**Used:** `{}`
**Free:** `{}`

**📊 Data Usage 📊**
**Upload:** `{}`
**Download:** `{}`

**📈 Memory Usage 📈**
**CPU:** `{}`
**RAM:** `{}`
**DISK:** `{}`
"""

usage_simple = """
**🖥️ Uptime 🖥️**
**App:** `{}`
**System:** `{}`

**💾 Disk Space 💾**
**Total:** `{}`
**Used:** `{}`
**Free:** `{}`

**📊 Data Usage 📊**
**Upload:** `{}`
**Download:** `{}`

**📈 Memory Usage 📈**
**CPU:** `{}`
**RAM:** `{}`
**DISK:** `{}`
"""

useragent = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0",
    "Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) "
    "Chrome/19.0.1084.46 Safari/536.5",
    "Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) " "Chrome/19.0.1084.46 Safari/536.5",
    "Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
]


@kasta_cmd(pattern="usage(?: |$)(.*)")
async def _(e):
    with suppress(BaseException):
        Kst = await e.eor("`Processing...`")
        try:
            opt = e.text.split(" ", maxsplit=1)[1]
        except IndexError:
            return await Kst.eor(simple_usage())
        if opt in ["heroku", "hk", "h"]:
            _, hk = await heroku_usage()
            await Kst.eor(hk)
        else:
            await Kst.eor(simple_usage())


def simple_usage():
    app_uptime = time_formatter((time() - StartTime) * 1000)
    system_uptime = datetime.fromtimestamp(psu.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    total, used, free = shu.disk_usage(".")
    cpu_freq = psu.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = "{}GHz".format(round(cpu_freq / 1000, 2))
    else:
        cpu_freq = "{}MHz".format(round(cpu_freq, 2))
    CPU = "{}% ({}) {}".format(psu.cpu_percent(interval=0.5), psu.cpu_count(), cpu_freq)
    RAM = "{}%".format(psu.virtual_memory().percent)
    DISK = "{}%".format(psu.disk_usage("/").percent)
    UPLOAD = humanbytes(psu.net_io_counters().bytes_sent)
    DOWN = humanbytes(psu.net_io_counters().bytes_recv)
    TOTAL = humanbytes(total)
    USED = humanbytes(used)
    FREE = humanbytes(free)
    return usage_simple.format(
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


async def heroku_usage():
    if not Var.HEROKU_API:
        return False, "Please set `HEROKU_API` in Config Vars."
    if not Var.HEROKU_APP_NAME:
        return False, "Please set `HEROKU_APP_NAME` in Config Vars."
    try:
        heroku_conn = from_key(Var.HEROKU_API)
        user_id = heroku_conn.account().id
    except Exception as err:
        return False, f"**ERROR**\n`{err}`"
    headers = {
        "User-Agent": choice(useragent),
        "Authorization": f"Bearer {Var.HEROKU_API}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    base_url = f"https://api.heroku.com/accounts/{user_id}/actions/get-quota"
    res = await Searcher(base_url, headers=headers, re_json=True)
    if not res:
        return False, "`Try again now!`"
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
    app_uptime = time_formatter((time() - StartTime) * 1000)
    system_uptime = datetime.fromtimestamp(psu.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    total, used, free = shu.disk_usage(".")
    cpu_freq = psu.cpu_freq().current
    if cpu_freq >= 1000:
        cpu_freq = "{}GHz".format(round(cpu_freq / 1000, 2))
    else:
        cpu_freq = "{}MHz".format(round(cpu_freq, 2))
    CPU = "{}% ({}) {}".format(psu.cpu_percent(interval=0.5), psu.cpu_count(), cpu_freq)
    RAM = "{}%".format(psu.virtual_memory().percent)
    DISK = "{}%".format(psu.disk_usage("/").percent)
    UPLOAD = humanbytes(psu.net_io_counters().bytes_sent)
    DOWN = humanbytes(psu.net_io_counters().bytes_recv)
    TOTAL = humanbytes(total)
    USED = humanbytes(used)
    FREE = humanbytes(free)
    return True, usage.format(
        app_uptime,
        system_uptime,
        Var.HEROKU_APP_NAME,
        AppHours,
        AppMinutes,
        AppPercentage,
        hours,
        minutes,
        percentage,
        TOTAL,
        USED,
        FREE,
        UPLOAD,
        DOWN,
        CPU,
        RAM,
        DISK,
    )


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
