# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
from io import BytesIO
from random import choice
from time import monotonic

from . import (
    CHROME_BIN,
    CHROME_DRIVER,
    Root,
    get_random_hex,
    import_lib,
    is_termux,
    is_url,
    kasta_cmd,
    plugins_help,
    time_formatter,
)


@kasta_cmd(
    pattern="ss(?: |$)(.*)",
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid link!`", time=5)
    toss = link
    check_link = is_url(toss)
    if not (check_link is True):
        toss = f"http://{link}"
        check_link = is_url(toss)
    if not (check_link is True):
        return await kst.eod("`Input is not supported link!`")
    yy = await kst.eor("`Processing...`")
    try:
        from selenium import webdriver
    except ImportError:
        if is_termux():
            return await kst.eor("`This command doesn't not supported Termux. Use proot-distro instantly!`", time=5)
        webdriver = import_lib(
            lib_name="selenium.webdriver",
            pkg_name="selenium==4.33.0",
        )
    start_time = monotonic()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--test-type")
    options.add_argument("--disable-logging")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.127 Safari/537.36"
    )
    prefs = {"download.default_directory": "./"}
    options.add_experimental_option("prefs", prefs)
    options.binary_location = CHROME_BIN
    await yy.eor("`Taking Screenshot...`")
    driver = webdriver.Chrome(
        service=webdriver.chrome.service.Service(executable_path=CHROME_DRIVER),
        options=options,
    )
    driver.get(toss)
    driver.execute_script("document.documentElement.style.overflow = 'hidden';document.body.style.overflow = 'hidden';")
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
    driver.quit()
    taken = time_formatter((monotonic() - start_time) * 1000)
    with BytesIO(ss_png) as file:
        file.name = f"ss_{link}.png"
        await yy.eor(
            f"**URL:** `{link}`\n**Taken:** `{taken}`",
            file=file,
            force_document=True,
        )


@kasta_cmd(
    pattern="tss(?: |$)(.*)",
)
async def _(kst):
    link = await kst.client.get_text(kst)
    if not link:
        return await kst.eor("`Provide a valid tweet link!`", time=5)
    toss = link
    check_link = is_url(toss)
    if not (check_link is True):
        toss = f"http://{link}"
        check_link = is_url(toss)
    try:
        import tweetcapture
    except ImportError:
        if is_termux():
            return await kst.eor("`This command doesn't not supported Termux. Use proot-distro instantly!`", time=5)
        tweetcapture = import_lib(
            lib_name="tweetcapture",
            pkg_name="tweet-capture==0.2.5",
        )
    if not (check_link is True) or not tweetcapture.utils.utils.is_valid_tweet_url(link):
        return await kst.eod("`Input is not valid tweet link!`")
    yy = await kst.eor("`Processing...`")
    start_time = monotonic()
    tweet = tweetcapture.TweetCapture()
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
        return await yy.eod("`Oops, the tweet not found or suspended account.`")
    await yy.eor("`Tweet Screenshot Taked...`")
    taken = time_formatter((monotonic() - start_time) * 1000)
    await yy.eor(
        f"**URL:** `{link}`\n**Taken:** `{taken}`",
        file=file,
        force_document=False,
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
