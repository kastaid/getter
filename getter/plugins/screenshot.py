# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import asyncio
import time
from io import BytesIO
from . import (
    Root,
    kasta_cmd,
    plugins_help,
    is_url,
    choice,
    is_termux,
    time_formatter,
    get_random_hex,
    import_lib,
    CHROME_BIN,
    CHROME_DRIVER,
)


@kasta_cmd(
    pattern="ss(?: |$)(.*)",
)
async def _(kst):
    try:
        import selenium
    except ImportError:
        if is_termux():
            await kst.eor("`This command doesn't not supported Termux. Use proot-distro instantly!`", time=5)
            return
        selenium = import_lib("selenium==4.4.3")
    link = await kst.client.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid link!`", time=5)
        return
    toss = link
    check_link = is_url(toss)
    if not (check_link is True):
        toss = f"http://{link}"
        check_link = is_url(toss)
    if not (check_link is True):
        return await kst.eod("`Input is not supported link!`")
    yy = await kst.eor("`Processing...`")
    start_time = time.time()
    options = selenium.webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--test-type")
    options.add_argument("--disable-logging")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    )
    prefs = {"download.default_directory": "./"}
    options.add_experimental_option("prefs", prefs)
    options.binary_location = CHROME_BIN
    await yy.eor("`Taking Screenshot...`")
    service = selenium.webdriver.chrome.service.Service(executable_path=CHROME_DRIVER)
    driver = selenium.webdriver.Chrome(service=service, options=options)
    driver.get(toss)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
    )
    driver.set_window_size(width + 125, height + 125)
    wait_for = height / 1000
    await asyncio.sleep(int(wait_for))
    ss_png = driver.get_screenshot_as_png()
    await yy.eor("`Screenshot Taked...`")
    driver.close()
    taken = time_formatter((time.time() - start_time) * 1000)
    with BytesIO(ss_png) as file:
        file.name = f"ss_{link}.png"
        await yy.eor(
            f"**URL:** `{link}`\n**Taken:** `{taken}`",
            file=file,
            force_document=True,
            allow_cache=False,
        )


@kasta_cmd(
    pattern="tss(?: |$)(.*)",
)
async def _(kst):
    try:
        from tweetcapture import TweetCapture
        from tweetcapture.utils import is_valid_tweet_url
    except ImportError:
        if is_termux():
            await kst.eor("`This command doesn't not supported Termux. Use proot-distro instantly!`", time=5)
            return
        TweetCapture = import_lib("tweet-capture==0.1.7").TweetCapture
        from tweetcapture.utils import is_valid_tweet_url
    link = await kst.client.get_text(kst)
    if not link:
        await kst.eor("`Provide a valid tweet link!`", time=5)
        return
    toss = link
    check_link = is_url(toss)
    if not (check_link is True):
        toss = f"http://{link}"
        check_link = is_url(toss)
    if not (check_link is True) or not is_valid_tweet_url(link):
        return await kst.eod("`Input is not valid tweet link!`")
    yy = await kst.eor("`Processing...`")
    start_time = time.time()
    tweet = TweetCapture()
    tweet.set_chromedriver_path(CHROME_DRIVER)
    tweet.add_chrome_argument("--no-sandbox")
    try:
        await yy.eor("`Taking Tweet Screenshot...`")
        file = await tweet.screenshot(
            link,
            f"tss_{get_random_hex()}.png",
            mode=2,
            night_mode=choice((0, 1, 2)),
        )
    except BaseException:
        await yy.eod("`Oops, the tweet not found or suspended account.`")
        return
    await yy.eor("`Tweet Screenshot Taked...`")
    taken = time_formatter((time.time() - start_time) * 1000)
    await yy.eor(
        f"**URL:** `{link}`\n**Taken:** `{taken}`",
        file=file,
        force_document=False,
        allow_cache=False,
    )
    (Root / file).unlink(missing_ok=True)


plugins_help["screenshot"] = {
    "{i}ss [link]/[reply]": "Take a full screenshot of website.",
    "{i}tss [link]/[reply]": """Gives screenshot of tweet.

**Examples:**
- Take a screenshot of website.
-> `{i}ss https://google.com`

- Take a screenshot of tweet.
-> `{i}tss https://twitter.com/jack/status/969234275420655616`
""",
}
