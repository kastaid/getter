# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import os
import time
from contextlib import suppress
from io import BytesIO
from validators.url import url
from . import (
    HELP,
    kasta_cmd,
    choice,
    time_formatter,
    get_random_hex,
    CHROME_BIN,
    CHROME_DRIVER,
)


@kasta_cmd(
    pattern="ss(?: |$)(.*)",
)
async def _(kst):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
    except ImportError:
        return
    to_ss = kst.pattern_match.group(1)
    if not to_ss:
        return await kst.try_delete()
    msg = await kst.eor("`Processing...`")
    start_time = time.time()
    toss = to_ss
    urlss = url(toss)
    if not urlss:
        toss = f"http://{to_ss}"
        urlss = url(toss)
    if not urlss:
        return await msg.eod("`Input is not supported url.`")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--test-type")
    options.add_argument("--disable-logging")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    )
    options.binary_location = CHROME_BIN
    msg = await msg.eor("`Taking Screenshot...`")
    service = Service(executable_path=CHROME_DRIVER)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(toss)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
    )
    driver.set_window_size(width + 100, height + 100)
    ss_png = driver.get_screenshot_as_png()
    msg = await msg.eor("`Screenshot Taked...`")
    driver.close()
    taken = time_formatter((time.time() - start_time) * 1000)
    with suppress(BaseException):
        with BytesIO(ss_png) as file:
            file.name = f"ss_{to_ss}.png"
            caption = rf"""\\**#Getter**//
**URL:** `{to_ss}`
**Taken:** `{taken}`"""
            await kst.client.send_file(
                kst.chat_id,
                file=file,
                caption=caption,
                force_document=True,
                allow_cache=False,
                reply_to=kst.reply_to_msg_id or kst.id,
                silent=True,
            )
    driver.quit()
    await msg.try_delete()


@kasta_cmd(
    pattern="tss(?: |$)(.*)",
)
async def _(kst):
    try:
        from tweetcapture import TweetCapture
        from tweetcapture.utils.utils import is_valid_tweet_url
    except ImportError:
        return
    to_ss = kst.pattern_match.group(1)
    if not to_ss:
        return await kst.try_delete()
    msg = await kst.eor("`Processing...`")
    start_time = time.time()
    if not is_valid_tweet_url(to_ss):
        return await msg.eod("`Input is not valid tweet url.`")
    msg = await msg.eor("`Taking Tweet Screenshot...`")
    tweet = TweetCapture()
    tweet.set_chromedriver_path(CHROME_DRIVER)
    tweet.add_chrome_argument("--no-sandbox")
    try:
        file = await tweet.screenshot(
            to_ss,
            f"tss_{get_random_hex()}.png",
            mode=2,
            night_mode=choice((0, 1, 2)),
        )
    except BaseException:
        await msg.eod("`Oops, the tweet not found or suspended account.`")
        return
    msg = await msg.eor("`Tweet Screenshot Taked...`")
    taken = time_formatter((time.time() - start_time) * 1000)
    with suppress(BaseException):
        caption = rf"""\\**#Getter**//
**URL:** `{to_ss}`
**Taken:** `{taken}`"""
        await kst.client.send_file(
            kst.chat_id,
            file=file,
            caption=caption,
            force_document=True,
            allow_cache=False,
            reply_to=kst.reply_to_msg_id or kst.id,
            silent=True,
        )
    if os.path.exists(file):
        os.remove(file)
    await msg.try_delete()


HELP.update(
    {
        "screenshot": [
            "Screenshot",
            """❯ `{i}ss <link>`
Take a full screenshot of a website.
**Example:** `{i}ss https://google.com`

❯ `{i}tss <twitter_link>`
Gives screenshot of tweet.
**Example:** `{i}tss https://twitter.com/jack/status/969234275420655616`
""",
        ]
    }
)
