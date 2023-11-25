# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import re
import typing
from functools import reduce
from math import ceil
from random import choice
from string import ascii_letters, ascii_uppercase, ascii_lowercase
from time import time
from uuid import uuid4
from bs4 import BeautifulSoup
from cachetools import cached
from emoji import replace_emoji
from markdown.core import markdown


def humanbool(b: typing.Any, toggle: bool = False) -> str:
    return ("off" if toggle else "no") if str(b).lower() in ("false", "none", "0", "") else ("on" if toggle else "yes")


def replace_all(
    text: str,
    repls: dict,
    regex: bool = False,
) -> str:
    if regex:
        return reduce(lambda a, kv: re.sub(*kv, a, flags=re.I), repls.items(), text)
    return reduce(lambda a, kv: a.replace(*kv), repls.items(), text)


def md_to_html(text: str) -> str:
    repls = {
        "<p>(.*)</p>": "\\1",
        r"\~\~(.*)\~\~": "<del>\\1</del>",
        r"\-\-(.*)\-\-": "<u>\\1</u>",
        r"\_\_(.*)\_\_": "<em>\\1</em>",
        r"\|\|(.*)\|\|": "<spoiler>\\1</spoiler>",
    }
    return replace_all(markdown(text), repls, regex=True)


def strip_format(text: str) -> str:
    repls = {
        "~~": "",
        "--": "",
        "__": "",
        "||": "",
    }
    return replace_all(BeautifulSoup(markdown(text), features="html.parser").get_text(), repls).strip()


def strip_emoji(text: str) -> str:
    return replace_emoji(text, "").strip()


def strip_ascii(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def humanbytes(size: typing.Union[int, float]) -> str:
    if not size:
        return "0 B"
    power = 1024
    pos = 0
    power_dict = {
        0: "",
        1: "K",
        2: "M",
        3: "G",
        4: "T",
        5: "P",
        6: "E",
        7: "Z",
        8: "Y",
    }
    while size > power:
        size /= power
        pos += 1
    return "{:.2f}{}B".format(size, power_dict[pos])


def time_formatter(ms: typing.Union[int, float]) -> str:
    minutes, seconds = divmod(int(ms / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w, ") if weeks else "")
        + ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp and tmp[:-2] or "0s"


def until_time(
    timing: typing.Union[str, int],
    unit: str = "m",
) -> typing.Tuple[float, str]:
    if unit.lower() not in (
        "s",
        "m",
        "h",
        "d",
        "w",
    ):
        unit = "m"
    if not str(timing).isdecimal():
        raise TypeError("'timing' must be integers or str digits")
    if unit == "s":
        until = int(time() + int(timing) * 1)
        dur = "seconds"
    elif unit == "m":
        until = int(time() + int(timing) * 60)
        dur = "minutes"
    elif unit == "h":
        until = int(time() + int(timing) * 60 * 60)
        dur = "hours"
    elif unit == "d":
        until = int(time() + int(timing) * 24 * 60 * 60)
        dur = "days"
    else:
        until = int(time() + int(timing) * 7 * 24 * 60 * 60)
        dur = "weeks"
    return until, dur


def get_random_hex(length: int = 12) -> str:
    return uuid4().hex[:length]


def get_random_alpha(length: int = 12) -> str:
    return "".join(choice(ascii_letters) for _ in range(length))


def mask_email(email: str) -> str:
    at = email.find("@")
    return email[0] + "*" * int(at - 2) + email[at - 1 :]


def chunk(lst: list, size: int = 2) -> list:
    return [lst[_ * size : _ * size + size] for _ in list(range(ceil(len(lst) / size)))]


def sort_dict(dct: dict, reverse: bool = False) -> dict:
    return dict(sorted(dct.items(), reverse=reverse))


def deep_get(
    dct: dict,
    keys: str,
    default: typing.Any = None,
) -> typing.Any:
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dct)


def to_dict(
    obj: typing.Any,
    classkey: typing.Optional[str] = None,
) -> typing.Any:
    if isinstance(obj, dict):
        data = {}
        for k, v in obj.items():
            data[k] = to_dict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(_, classkey) for _ in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(  # noqa
            [(k, to_dict(v, classkey)) for k, v in obj.__dict__.items() if not callable(v) and not k.startswith("_")]
        )
        if classkey and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    return obj


def camel(text: str) -> str:
    text = re.sub(r"(_|-)+", " ", text).title().replace(" ", "")
    return "".join([text[0].lower(), text[1:]])


def snake(text: str) -> str:
    return "_".join(re.sub("([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", text.replace("-", " "))).split()).lower()


def kebab(text: str) -> str:
    return "-".join(
        re.sub(
            r"(\s|_|-)+",
            " ",
            re.sub(
                r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                lambda x: " " + x.group(0).lower(),
                text,
            ),
        ).split()
    )


@cached(cache={})
def normalize(text: str) -> str:
    normal = text
    uppercase = tuple(ascii_uppercase)
    lowercase = tuple(ascii_lowercase)
    f1 = tuple("𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ")
    f2 = tuple("𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅")
    f3 = tuple("𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩")
    f4 = tuple("𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵")
    f5 = tuple("𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ")
    f6 = tuple("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ")
    f7 = tuple("𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")
    f8 = tuple("𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭")
    f9 = tuple("𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡")
    f10 = tuple("𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕")
    f11 = tuple("𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉")
    f12 = tuple("𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷")
    f13 = tuple("𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟")
    f14 = tuple("𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃")
    f15 = tuple("𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏")
    f16 = tuple("𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫")
    f17 = tuple("ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ")
    f18 = tuple("𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳")
    f19 = tuple("𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇")
    f20 = tuple("𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻")
    f21 = tuple("𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯")
    f22 = tuple("𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣")
    f23 = tuple("𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁")
    f24 = tuple("𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛")
    f25 = tuple("ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀsᴛᴜᴠᴡxʏᴢ")
    f26 = tuple("ʌʙᴄᴅᴇғɢʜıᴊᴋʟᴍɴᴏᴘϙʀsᴛᴜᴠᴡxʏᴢ")
    f27 = tuple("🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉")
    f28 = tuple("ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ")
    for count, _ in enumerate(uppercase):
        normal = normal.replace(f1[count], uppercase[count])
        normal = normal.replace(f2[count], uppercase[count])
        normal = normal.replace(f3[count], uppercase[count])
        normal = normal.replace(f4[count], uppercase[count])
        normal = normal.replace(f5[count], uppercase[count])
        normal = normal.replace(f6[count], uppercase[count])
        normal = normal.replace(f7[count], uppercase[count])
        normal = normal.replace(f8[count], uppercase[count])
        normal = normal.replace(f9[count], uppercase[count])
        normal = normal.replace(f10[count], uppercase[count])
        normal = normal.replace(f11[count], uppercase[count])
        normal = normal.replace(f12[count], lowercase[count])
        normal = normal.replace(f13[count], lowercase[count])
        normal = normal.replace(f14[count], lowercase[count])
        normal = normal.replace(f15[count], lowercase[count])
        normal = normal.replace(f16[count], lowercase[count])
        normal = normal.replace(f17[count], lowercase[count])
        normal = normal.replace(f18[count], lowercase[count])
        normal = normal.replace(f19[count], lowercase[count])
        normal = normal.replace(f20[count], lowercase[count])
        normal = normal.replace(f21[count], lowercase[count])
        normal = normal.replace(f22[count], lowercase[count])
        normal = normal.replace(f23[count], uppercase[count])
        normal = normal.replace(f24[count], lowercase[count])
        normal = normal.replace(f25[count], uppercase[count])
        normal = normal.replace(f26[count], uppercase[count])
        normal = normal.replace(f27[count], uppercase[count])
        normal = normal.replace(f28[count], lowercase[count])
        count += 1
    return " ".join(strip_ascii(normal).split())


def get_full_class_name(obj: typing.Any) -> str:
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__
