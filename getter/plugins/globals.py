# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from asyncio import sleep
from contextlib import suppress
from io import BytesIO
from re import sub
from secrets import choice
from time import time
from telethon.errors import FloodWaitError
from . import (
    DEVS,
    HELP,
    kasta_cmd,
    time_formatter,
    Searcher,
)


async def nospam_chat():
    base_url = "https://raw.githubusercontent.com/kastaid/resources/main/gcastblacklist.py"
    count = 0
    retry = 6
    while count < retry:
        r = await Searcher(base_url, re_content=True)
        count += 1
        if not r:
            if count != retry:
                await sleep(1)
                continue
            ids = [
                -1001699144606,  # @kastaot
                -1001700971911,  # @kastaup
                -1001596433756,  # @MFIChat
                -1001294181499,  # @userbotindo
                -1001387666944,  # @PyrogramChat
                -1001221450384,  # @pyrogramlounge
                -1001109500936,  # @TelethonChat
                -1001235155926,  # @RoseSupportChat
                -1001421589523,  # @tdspya
                -1001360494801,  # @OFIOpenChat
                -1001435671639,  # @xfichat
            ]
            break
        _ = r"(\[|\]|#.[\w]*|,)"
        ids = set(int(x) for x in sub(_, " ", "".join(r.decode("utf-8").split())).split())  # noqa: C401
        break
    return ids


@kasta_cmd(pattern=r"g(admin|)cast(?:\s|$)([\s\S]*)")
@kasta_cmd(own=True, senders=DEVS, pattern=r"gg(admin|)cast(?:\s|$)([\s\S]*)")
async def _(e):
    is_admin = True if e.text and e.text[2:7] == "admin" or e.text[3:8] == "admin" else False
    match = e.pattern_match.group(2)
    if match:
        content = match
    elif e.is_reply:
        content = await e.get_reply_message()
    else:
        return await e.eod("`Give some text to Gcast or reply message.`")
    if is_admin:
        Kst = await e.eor("⚡ __**Gcasting to groups as admin...**__")
    else:
        Kst = await e.eor("⚡ __**Gcasting to all groups...**__")
    start_time = time()
    success = failed = 0
    error = ""
    NOSPAM_CHAT = await nospam_chat()
    async for x in e.client.iter_dialogs():
        if x.is_group:
            chat = x.entity.id
            if int("-100" + str(chat)) not in NOSPAM_CHAT and (
                not is_admin or (x.entity.admin_rights or x.entity.creator)
            ):
                try:
                    await e.client.send_message(chat, content)
                    await sleep(choice((2, 4, 6)))
                    success += 1
                except FloodWaitError as fw:
                    await sleep(fw.seconds + 10)
                    try:
                        await e.client.send_message(chat, content)
                        await sleep(choice((2, 4, 6)))
                        success += 1
                    except Exception as err:
                        error += f"• {err}\n"
                        failed += 1
                except Exception as err:
                    error += "• " + str(err) + "\n"
                    failed += 1
    taken = time_formatter((time() - start_time) * 1000)
    text = r"\\**#Gcast**// `{}` to `{}` {}, failed `{}` groups.".format(
        taken,
        success,
        "groups as admin" if is_admin else "groups",
        failed,
    )
    with suppress(BaseException):
        if error != "":
            with BytesIO(str.encode(error)) as file:
                file.name = "gcast-error.log"
                await e.client.send_file(
                    e.chat_id or e.from_id,
                    file=error,
                    caption="Gcast Error Logs",
                    force_document=True,
                    allow_cache=False,
                )
    await Kst.eor(text)


HELP.update(
    {
        "globals": [
            "Globals",
            """❯ `{i}gcast <text/reply>`
Send broadcast messages to all groups.

❯ `{i}gadmincast <text/reply>`
Same as above, but only in your admin groups.

**DWYOR ~ Do With Your Own Risk!**
""",
        ]
    }
)
