# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from . import (
    gvar,
    kasta_cmd,
    plugins_help,
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
    username = await gvar("ig") or "illvart_"
    if hah == "u":
        ig = f"𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌  ➥  `@{username}`"
    else:
        ig = f"𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌  ➥  [@{username}](https://www.instagram.com/{username})"
    await kst.sod(ig)


@kasta_cmd(
    pattern="sfs(p|u|)$",
)
async def _(kst):
    hah = kst.pattern_match.group(1).strip()
    username = await gvar("sfs") or "kastaid"
    if hah == "p":
        sfs = f"𝐒𝐔𝐁𝐒 𝐅𝐎𝐑 𝐒𝐔𝐁𝐒  ➥  `t.me/{username}`"
    elif hah == "u":
        sfs = f"𝐒𝐔𝐁𝐒 𝐅𝐎𝐑 𝐒𝐔𝐁𝐒  ➥  `@{username}`"
    else:
        sfs = f"𝐒𝐔𝐁𝐒 𝐅𝐎𝐑 𝐒𝐔𝐁𝐒  ➥  [@{username}](https://t.me/{username})"
    await kst.sod(sfs)


@kasta_cmd(
    pattern="set(ig|sfs)(?: |$)(.*)",
)
async def _(kst):
    var = kst.pattern_match.group(1)
    val = await kst.client.get_text(kst, group=2)
    forwhat = await gvar(var) or ""
    if not val:
        forwhat = forwhat or "illvart_" if var == "ig" else forwhat or "kastaid"
        return await kst.eor(f"**{var.upper()}:** `{forwhat}`")
    val = val.replace("@", "")
    if var == "ig":
        if val == forwhat:
            return await kst.eor("`IG is already set.`", time=4)
        await sgvar(var, val)
        return await kst.eod(f"`IG set to {val}.`")
    if val == forwhat:
        return await kst.eor("`SFS is already set.`", time=4)
    await sgvar(var, val)
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
