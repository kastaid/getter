# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from . import (
    FUN_APIS,
    Fetch,
    deep_get,
    formatx_send,
    kasta_cmd,
    plugins_help,
)


@kasta_cmd(
    pattern="get(cat|dog|food|neko|waifu|neko18|waifu18|blowjob|cringe|cry|dance|happy|fact|quote)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    yy = await kst.eor("`Processing...`")
    api = FUN_APIS[cmd]
    url = api.get("url")
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    try:
        if isinstance(res, list):
            res = next((_ for _ in res), {})
        out = deep_get(res, api.get("value"))
        if api.get("type") == "text":
            source = api.get("source")
            if source:
                out += f"\n~ {res.get(source)}"
            await yy.eor(out)
        else:
            await yy.eor(
                file=out,
                force_document=False,
            )
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


plugins_help["randoms"] = {
    "{pfx}getcat": "Random cat image.",
    "{pfx}getdog": "Random dog image.",
    "{pfx}getfood": "Random food image.",
    "{pfx}getneko": "Random neko image.",
    "{pfx}getwaifu": "Random waifu image.",
    "{pfx}getneko18": "Random neko nsfw image.",
    "{pfx}getwaifu18": "Random waifu nsfw image.",
    "{pfx}getblowjob": "Random blowjob nsfw image.",
    "{pfx}getcringe": "Random anime cringe gif.",
    "{pfx}getcry": "Random anime cry gif.",
    "{pfx}getdance": "Random anime dance gif.",
    "{pfx}gethappy": "Random anime happy gif.",
    "{pfx}getfact": "Random fun facts.",
    "{pfx}getquote": "Random quotes.",
}
