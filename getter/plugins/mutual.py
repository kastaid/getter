# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from . import (
    kasta_cmd,
    plugins_help,
    gvar,
    sgvar,
)


@kasta_cmd(
    pattern="dea(c|k)$",
)
async def _(kst):
    deak = "**[Deactivate Telegram Account](https://telegram.org/deactivate)**"
    await kst.sod(deak)


@kasta_cmd(
    pattern="ig(u|)$",
)
async def _(kst):
    hah = kst.pattern_match.group(1).strip()
    username = gvar("ig") or "illvart_"
    if hah == "u":
        ig = "𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌  ➥  `@{}`".format(username)
    else:
        ig = "𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌  ➥  [@{}](https://www.instagram.com/{})".format(username, username)
    await kst.sod(ig)


@kasta_cmd(
    pattern="sfs(p|u|)$",
)
async def _(kst):
    hah = kst.pattern_match.group(1).strip()
    username = gvar("sfs") or "kastaid"
    if hah == "p":
        sfs = "𝐒𝐔𝐁𝐒 𝐅𝐎𝐑 𝐒𝐔𝐁𝐒  ➥  `t.me/{}`".format(username)
    elif hah == "u":
        sfs = "𝐒𝐔𝐁𝐒 𝐅𝐎𝐑 𝐒𝐔𝐁𝐒  ➥  `@{}`".format(username)
    else:
        sfs = "𝐒𝐔𝐁𝐒 𝐅𝐎𝐑 𝐒𝐔𝐁𝐒  ➥  [@{}](https://t.me/{})".format(username, username)
    await kst.sod(sfs)


@kasta_cmd(
    pattern="set(ig|sfs)(?: |$)(.*)",
)
async def _(kst):
    var = kst.pattern_match.group(1)
    val = await kst.client.get_text(kst, group=2)
    forwhat = gvar(var) or ""
    if not val:
        if var == "ig":
            forwhat = forwhat or "illvart_"
        else:
            forwhat = forwhat or "kastaid"
        text = "**{}:** `{}`".format(var.upper(), forwhat)
        await kst.eor(text)
        return
    val = val.replace("@", "")
    if var == "ig":
        if val == forwhat:
            await kst.eor("`IG is already set.`", time=4)
            return
        sgvar(var, val)
        await kst.eod(f"`IG set to {val}.`")
        return
    if val == forwhat:
        await kst.eor("`SFS is already set.`", time=4)
        return
    sgvar(var, val)
    await kst.eod(f"`SFS set to {val}.`")


plugins_help["mutual"] = {
    "{i}deak|{i}deac": "Get a link Deactivate Telegram Account.",
    "{i}ig": "My Instagram link.",
    "{i}igu": "My Instagram username.",
    "{i}sfs": "Do “subs for subs” to my Channel link.",
    "{i}sfsu": "My Channel username.",
    "{i}sfsp": "My Channel private link.",
    "{i}setig [username]": "Set or update my Instagram username without @.",
    "{i}setsfs [username]": "Set or update my Channel username without @. For a private link just put example `+Cfq2dypcEoQxN2U9`.",
}
