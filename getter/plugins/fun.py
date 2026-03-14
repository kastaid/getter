# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import asyncio
import html
import random
from collections import deque

from emoji import emojize
from telethon.tl import types as typ

from . import (
    SHRUGS,
    UWUS,
    kasta_cmd,
    parse_pre,
    plugins_help,
)

dices = emojize(":game_die: :bullseye: :basketball: :soccer_ball: :bowling: :slot_machine:").split()


@kasta_cmd(
    pattern="(roll|decide)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "roll":
        chars = range(1, 7)
    elif cmd == "decide":
        chars = ("yes", "no", "maybe")
    text = random.choice(chars)
    await kst.sod(str(text))


@kasta_cmd(
    pattern="owo$",
)
@kasta_cmd(
    pattern="owo$",
    sudo=True,
)
@kasta_cmd(
    pattern="owo$",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(random.choice((4, 6, 8)))
    text = html.escape(random.choice(UWUS))
    await kst.sod(f"<code>{text}</code>", parse_mode="html", silent=True)


@kasta_cmd(
    pattern="shg$",
)
@kasta_cmd(
    pattern="shg$",
    sudo=True,
)
@kasta_cmd(
    pattern="shg$",
    dev=True,
)
async def _(kst):
    if kst.is_dev or kst.is_sudo:
        await asyncio.sleep(random.choice((4, 6, 8)))
    text = html.escape(random.choice(SHRUGS))
    await kst.sod(f"<code>{text}</code>", parse_mode="html", silent=True)


@kasta_cmd(
    pattern="(ran|bol|bas|bow|dic|dar|slot)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "ran":
        dice = random.choice(dices)
    if cmd == "bol":
        dice = ":soccer_ball:"
    elif cmd == "bas":
        dice = ":basketball:"
    elif cmd == "bow":
        dice = ":bowling:"
    elif cmd == "dic":
        dice = ":game_die:"
    elif cmd == "dar":
        dice = ":bullseye:"
    elif cmd == "slot":
        dice = ":slot_machine:"
    async with await kst.send_action(action="game"):
        await kst.eor(file=typ.InputMediaDice(emojize(dice)))
        await asyncio.sleep(2)


@kasta_cmd(
    pattern="(love|fap|star|moon|think|lul|clock|muah|gym|earth|candy|rain|run|boxs)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "love":
        emot = "❤️🧡💛💚💙💜🖤"
    elif cmd == "fap":
        emot = "👉👌💦"
    elif cmd == "star":
        emot = "🦋✨🦋✨🦋✨🦋✨"
    elif cmd == "moon":
        emot = "🌗🌘🌑🌒🌓🌔🌕🌖"
    elif cmd == "think":
        emot = "🤔🧐🤔🧐🤔🧐"
    elif cmd == "lul":
        emot = "😂🤣😂🤣😂🤣"
    elif cmd == "clock":
        emot = "🕙🕘🕗🕖🕕🕔🕓🕒🕑🕐🕛"
    elif cmd == "muah":
        emot = "😗😙😚😚😘"
    elif cmd == "gym":
        emot = "🏃‍🏋‍🤸‍🏃‍🏋‍🤸‍🏃‍🏋‍🤸‍"
    elif cmd == "earth":
        emot = "🌏🌍🌎🌎🌍🌏🌍🌎"
    elif cmd == "candy":
        emot = "🍦🍧🍩🍪🎂🍰🧁🍫🍬🍭"
    elif cmd == "rain":
        emot = "☀️🌤️⛅🌥️☁️🌩️🌧️⛈️⚡🌩️🌧️🌦️🌥️⛅🌤️☀️"
    elif cmd == "run":
        emot = "🚶🏃🚶🏃🚶🏃🚶🏃"
    elif cmd == "boxs":
        emot = "🟥🟧🟨🟩🟦🟪🟫⬛⬜"
    deq = deque(emot)
    for _ in range(48):
        await asyncio.sleep(0.2)
        await kst.eor("".join(deq))
        deq.rotate(1)


@kasta_cmd(
    pattern="heart$",
)
async def _(kst):
    chars = (
        "❤️",
        "🧡",
        "💛",
        "💚",
        "💙",
        "💜",
        "🖤",
        "💘",
        "💝",
        "❤️",
        "🧡",
        "💛",
        "💚",
        "💙",
        "💜",
        "🖤",
        "💘",
        "💝",
    )
    yy = await kst.eor("🖤")
    for x in range(54):
        await asyncio.sleep(0.5)
        await yy.eor(chars[x % 18])


@kasta_cmd(
    pattern="solars$",
)
async def _(kst):
    chars = (
        "◼️◼️◼️◼️◼️\n◼️◼️◼️◼️☀\n◼️◼️🌎◼️◼️\n🌕◼️◼️◼️◼️\n◼️◼️◼️◼️◼️",
        "◼️◼️◼️◼️◼️\n🌕◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️☀\n◼️◼️◼️◼️◼️",
        "◼️🌕◼️◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️◼️☀◼️",
        "◼️◼️◼️🌕◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️☀◼️◼️◼️",
        "◼️◼️◼️◼️◼️\n◼️◼️◼️◼️🌕\n◼️◼️🌎◼️◼️\n☀◼️◼️◼️◼️\n◼️◼️◼️◼️◼️",
        "◼️◼️◼️◼️◼️\n☀◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️🌕\n◼️◼️◼️◼️◼️",
        "◼️☀◼️◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️◼️◼️🌕◼️",
        "◼️◼️◼️☀◼️\n◼️◼️◼️◼️◼️\n◼️◼️🌎◼️◼️\n◼️◼️◼️◼️◼️\n◼️🌕◼️◼️◼️",
    )
    yy = await kst.eor("`solarsystem...`")
    for x in range(80):
        await asyncio.sleep(0.3)
        await yy.eor(chars[x % 8], parse_mode=parse_pre)


@kasta_cmd(
    pattern="(kocok|dino)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "kocok":
        chars = (
            "8✊️===D",
            "8=✊️==D",
            "8==✊️=D",
            "8===✊️D",
            "8==✊️=D",
            "8=✊️==D",
            "8✊️===D",
            "8=✊️==D",
            "8==✊️=D",
            "8===✊️D",
            "8==✊️=D",
            "8=✊️==D",
            "8✊️===D",
            "8=✊️==D",
            "8==✊️=D",
            "8===✊️D",
            "8==✊️=D",
            "8=✊️==D",
            "8✊️===D",
            "8=✊️==D",
            "8==✊️=D",
            "8===✊️D",
            "8==✊️=D",
            "8=✊️==D",
            "8===✊D💦",
            "8==✊=D💦💦",
            "8=✊==D💦💦💦",
            "8✊===D💦💦💦💦",
            "8===✊D💦💦💦💦💦",
            "8==✊=D💦💦💦💦💦💦",
            "8=✊==D💦💦💦💦💦💦💦",
            "8✊===D💦💦💦💦💦💦💦💦",
            "8===✊D💦💦💦💦💦💦💦💦💦",
            "8==✊=D💦💦💦💦💦💦💦💦💦💦",
            "8=✊==D ?",
            "8==✊=D ??",
            "8===✊D ???",
            "😭😭😭",
        )
    elif cmd == "dino":
        chars = (
            "🏃                        🦖",
            "🏃                       🦖",
            "🏃                      🦖",
            "🏃                     🦖",
            "🏃                    🦖",
            "🏃                   🦖",
            "🏃                  🦖",
            "🏃                 🦖",
            "🏃                🦖",
            "🏃               🦖",
            "🏃              🦖",
            "🏃             🦖",
            "🏃            🦖",
            "🏃           🦖",
            "🏃          🦖",
            "🏃           🦖",
            "🏃            🦖",
            "🏃             🦖",
            "🏃              🦖",
            "🏃               🦖",
            "🏃                🦖",
            "🏃                 🦖",
            "🏃                  🦖",
            "🏃                   🦖",
            "🏃                    🦖",
            "🏃                     🦖",
            "🏃                    🦖",
            "🏃                   🦖",
            "🏃                  🦖",
            "🏃                 🦖",
            "🏃                🦖",
            "🏃               🦖",
            "🏃              🦖",
            "🏃             🦖",
            "🏃            🦖",
            "🏃           🦖",
            "🏃          🦖",
            "🏃         🦖",
            "🏃        🦖",
            "🏃       🦖",
            "🏃      🦖",
            "🏃     🦖",
            "🏃    🦖",
            "🏃   🦖",
            "🏃  🦖",
            "🏃 🦖",
            "🧎🦖",
        )
    for char in chars:
        await asyncio.sleep(0.3)
        await kst.eor(char, parse_mode=parse_pre)


@kasta_cmd(
    pattern="(dick|doggy|dog|fucku|rose|pki|pistol|ok)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "dick":
        art = """
ㅤ
⣠⡶⠚⠛⠲⢄⡀
⣼⠁ ⠀⠀⠀ ⠳⢤⣄
⢿⠀⢧⡀⠀⠀⠀⠀⠀⢈⡇
⠈⠳⣼⡙⠒⠶⠶⠖⠚⠉⠳⣄
⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄
⠀⠀⠀⠘⣆ ⠀⠀⠀ ⠀   ⠈⠓⢦⣀
⠀⠀⠀⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠲⢤
⠀⠀⠀⠀⠀⠀⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧
⠀⠀⠀⠀⠀⠀⠀⡴⠋⠓⠦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠈⣇
⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄
⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⢹⡄⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃
⠀⠀⠀⠀⠀⠀⠀⠙⢦⣀⣳⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⢦⣀⣀⣀⣀⣠⡴⠚⠉
ㅤ
"""
    elif cmd == "doggy":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⣠⣤⣄
⠀⠀⠀⠀⠀⢰⣿⣿⣿⡷
⠀⠀⠀⠀⠀⢀⣙⡛⠛⠁
⠀⠀⠀⠀⢀⣿⣿⣿⡆
⠀⠀⠀⠀⣾⣿⣿⣿⣧
⠀⠀⠀⢰⣿⣿⣿⠙⣿⣧⠀⣤⣶⣄⣾⣿⣿⣷
⠀⠀⠀⢻⣿⣿⣇⣴⣮⡿⣿⡟⠛⠁⣙⠿⠿⠋
⠀⠀⠀⠘⣿⣿⡏⣿⣿⣿⣾⣾⣿⣿⣿⣷
⢀⣀⣀⣀⣿⣿⡇⢿⣿⡇⠈⠉⠻⡿⣿⡏
⠘⠿⠿⠿⠿⠿⠧⠿⠿⠇⠀⠀⠀⠀⠿⠿⠿⠿⠗
ㅤ
"""
    elif cmd == "dog":
        art = r"""
ㅤ
┈┈┈┈╱▏┈┈┈┈┈╱▔▔▔▔╲┈┈┈┈
┈┈┈┈▏▏┈┈┈┈┈▏╲▕▋▕▋▏┈┈┈
┈┈┈┈╲╲┈┈┈┈┈▏┈▏┈▔▔▔▆┈┈
┈┈┈┈┈╲▔▔▔▔▔╲╱┈╰┳┳┳╯┈┈
┈┈╱╲╱╲▏┈┈┈┈┈┈▕▔╰━╯┈┈┈
┈┈▔╲╲╱╱▔╱▔▔╲╲╲╲┈┈┈┈┈┈
┈┈┈┈╲╱╲╱┈┈┈┈╲╲▂╲▂┈┈┈┈
┈┈┈┈┈┈┈┈┈┈┈┈┈╲╱╲╱┈┈┈┈
ㅤ
"""
    elif cmd == "fucku":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠏⠁⠙⢿⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⠀⣾⠏⣿⠀⠀⠀⠀⢸⣷⣦⣄⡀
⠀⠀⠀⠀⠀⠀⣼⡿⠀⣿⠀⠀⠀⠀⢸⠇⠀⠉⢷⡀
⠀⠀⠀⠀⣠⡾⢿⠇⠀⣿⠀⠀⠀⠀⢸⡇⠀⠀⠸⡷⠤⣄⡀
⠀⠀⢠⡾⠋⣾⠀⠀⠀⣿⠀⠀⠀⠀⢸⡇⠀⠀⠀⣧⠀⠀⠹⡄
⠀⣰⠏⠀⠀⣿⠀⠀⠀⠉⠀⠀⠀⠀⠈⠁⠀⠀⠀⢹⡄⠀⠀⢹⡄
⢰⡏⠀⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠇⠀⠀⠀⢻⡄
⠘⣿⡀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣷
⠀⠙⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿
⠀⠀⠀⠹⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡟
⠀⠀⠀⠀⠈⠻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠟
⠀⠀⠀⠀⠀⠀⠈⠻⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡿⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠏
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏⠀⠀⠀⠀⠀⠀⠀⠀⢸⡏
ㅤ
"""
    elif cmd == "rose":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀
⠀⠀⠀⠀⠀⠀⠀⡠⠖⠋⠉⠉⠳⡴⠒⠒⠒⠲⠤⢤⣀
⠀⠀⠀⠀⠀⣠⠊⠀⠀⡴⠚⡩⠟⠓⠒⡖⠲⡄⠀⠀⠈⡆
⠀⠀⠀⢀⡞⠁⢠⠒⠾⢥⣀⣇⣚⣹⡤⡟⠀⡇⢠⠀⢠⠇
⠀⠀⠀⢸⣄⣀⠀⡇⠀⠀⠀⠀⠀⢀⡜⠁⣸⢠⠎⣰⣃
⠀⠀⠸⡍⠀⠉⠉⠛⠦⣄⠀⢀⡴⣫⠴⠋⢹⡏⡼⠁⠈⠙⢦⡀
⠀⠀⣀⡽⣄⠀⠀⠀⠀⠈⠙⠻⣎⡁⠀⠀⣸⡾⠀⠀⠀⠀⣀⡹⠂
⢀⡞⠁⠀⠈⢣⡀⠀⠀⠀⠀⠀⠀⠉⠓⠶⢟⠀⢀⡤⠖⠋⠁
⠀⠉⠙⠒⠦⡀⠙⠦⣀⠀⠀⠀⠀⠀⠀⢀⣴⡷⠋
⠀⠀⠀⠀⠀⠘⢦⣀⠈⠓⣦⣤⣤⣤⢶⡟⠁
⢤⣤⣤⡤⠤⠤⠤⠤⣌⡉⠉⠁⠀⢸⢸⠁⡠⠖⠒⠒⢒⣒⡶⣶⠤
⠉⠲⣍⠓⠦⣄⠀⠀⠙⣆⠀⠀⠀⡞⡼⡼⢀⣠⠴⠊⢉⡤⠚⠁
⠀⠀⠈⠳⣄⠈⠙⢦⡀⢸⡀⠀⢰⢣⡧⠷⣯⣤⠤⠚⠉
⠀⠀⠀⠀⠈⠑⣲⠤⠬⠿⠧⣠⢏⡞
⠀⠀⢀⡴⠚⠉⠉⢉⣳⣄⣠⠏⡞
⣠⣴⣟⣒⣋⣉⣉⡭⠟⢡⠏⡼
⠉⠀⠀⠀⠀⠀⠀⠀⢀⠏⣸⠁
⠀⠀⠀⠀⠀⠀⠀⠀⡞⢠⠇
⠀⠀⠀⠀⠀⠀⠀⠘⠓⠚
ㅤ
"""
    elif cmd == "pki":
        art = """
ㅤ
⠀⠀⠀⠀⠀⠀⢀⣤⣀⣀⣀⠀⠻⣷⣄
⠀⠀⠀⠀⢀⣴⣿⣿⣿⡿⠋⠀⠀⠀⠹⣿⣦⡀
⠀⠀⢀⣴⣿⣿⣿⣿⣏⠀⠀⠀⠀⠀⠀⢹⣿⣧
⠀⠀⠙⢿⣿⡿⠋⠻⣿⣿⣦⡀⠀⠀⠀⢸⣿⣿⡆
⠀⠀⠀⠀⠉⠀⠀⠀⠈⠻⣿⣿⣦⡀⠀⢸⣿⣿⡇
⠀⠀⠀⠀⢀⣀⣄⡀⠀⠀⠈⠻⣿⣿⣶⣿⣿⣿⠁
⠀⠀⠀⣠⣿⣿⢿⣿⣶⣶⣶⣶⣾⣿⣿⣿⣿⡁
⢠⣶⣿⣿⠋⠀⠀⠉⠛⠿⠿⠿⠿⠿⠛⠻⣿⣿⣦⡀
⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⡿
ㅤ
"""
    elif cmd == "pistol":
        art = """
ㅤ
⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣤⣤
⠀⢶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿
⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠛⠛⠛⠛⠛⠋⠉
⠀⠀⢹⣿⣿⣿⣿⣿⠏⢠⣿⡀⠀⠀⢹⡟
⠀⢠⣿⣿⣿⣿⣿⣿⣦⣀⣀⣙⣂⣠⠼⠃
⠀⣾⣿⣿⣿⣿⣿⠁
⢠⣿⣿⣿⣿⣿⡟
⢸⣿⣿⣿⣿⣿⡅
⠀⠛⠛⠛⠛⠛⠃
ㅤ
"""
    elif cmd == "ok":
        art = """
ㅤ
⠀⠀⠀⠀⣠⣶⡾⠏⠉⠙⠳⢦⡀⠀⠀⠀⢠⠞⠉⠙⠲⡀
⠀⠀⠀⣴⠿⠏⠀⠀⠀⠀⠀⠀⢳⡀⠀⡏⠀⠀⠀⠀⠀⢷
⠀⠀⢠⣟⣋⡀⢀⣀⣀⡀⠀⣀⡀⣧⠀⢸⠀⠀⠀⠀⠀ ⡇
⠀⠀⢸⣯⡭⠁⠸⣛⣟⠆⡴⣻⡲⣿⠀⣸⠀⠀OK⠀ ⡇
⠀⠀⣟⣿⡭⠀⠀⠀⠀⠀⢱⠀⠀⣿⠀⢹⠀⠀⠀⠀⠀ ⡇
⠀⠀⠙⢿⣯⠄⠀⠀⠀⢀⡀⠀⠀⡿⠀⠀⡇⠀⠀⠀⠀⡼
⠀⠀⠀⠀⠹⣶⠆⠀⠀⠀⠀⠀⡴⠃⠀⠀⠘⠤⣄⣠⠞
⠀⠀⠀⠀⠀⢸⣷⡦⢤⡤⢤⣞⣁
⠀⠀⢀⣤⣴⣿⣏⠁⠀⠀⠸⣏⢯⣷⣖⣦⡀
⢀⣾⣽⣿⣿⣿⣿⠛⢲⣶⣾⢉⡷⣿⣿⠵⣿
⣼⣿⠍⠉⣿⡭⠉⠙⢺⣇⣼⡏⠀⠀⠀⣄⢸
⣿⣿⣧⣀⣿.........⣀⣰⣏⣘⣆⣀
ㅤ
"""
    await kst.sod(f"<code>{art}</code>", parse_mode="html")


@kasta_cmd(
    pattern="(baa|bgst)$",
)
async def _(kst):
    cmd = kst.pattern_match.group(1)
    if cmd == "baa":
        expr = """
┻┳|
┳┻| _
┻┳| •.•)  **baa**
┳┻|⊂ﾉ
┻┳|
"""
    elif cmd == "bgst":
        expr = """
○
く|)へ
    〉
 ￣￣┗┓             __bgst bgst__
 　 　   ┗┓　     ヾ○ｼ
  　　        ┗┓   ヘ/
 　                 ┗┓ノ
　 　 　 　 　   ┗┓
"""
    await kst.sod(expr)


@kasta_cmd(
    pattern="thinking$",
)
async def _(kst):
    chars = (
        "THINKING",
        "THI&K#N₹",
        "T+IN@I?G",
        "¿H$NK∆NG",
        "¶H×NK&N*",
        "NGITHKIN",
        "T+I#K@₹G",
        "THINKING",
        "THI&K#N₹",
        "T+IN@I?G",
        "¿H$NK∆NG",
        "¶H×NK&N*",
        "NGITHKIN",
        "T+I#K@₹G",
        "THINKING",
        "THI&K#N₹",
        "T+IN@I?G",
        "¿H$NK∆NG",
        "¶H×NK&N*",
        "NGITHKIN",
        "T+I#K@₹G",
        "THINKING",
        "THI&K#N₹",
        "T+IN@I?G",
        "¿H$NK∆NG",
        "¶H×NK&N*",
        "NGITHKIN",
        "T+I#K@₹G",
        "THINKING",
        "THI&K#N₹",
        "T+IN@I?G",
        "¿H$NK∆NG",
        "¶H×NK&N*",
        "NGITHKIN",
        "T+I#K@₹G",
        "THINKING...🤔",
    )
    yy = await kst.eor("`Thinking...`")
    for x in range(288):
        await asyncio.sleep(0.1)
        await yy.eor(chars[x % 36])


@kasta_cmd(
    pattern="durov$",
)
async def _(kst):
    chars = (
        "Connecting To Telegram Headquarters...",
        "Call Connected.",
        "Telegram: Hello This is Telegram HQ. Who is this?",
        f"Me: Yo this is {kst.client.full_name} , Please Connect me to my lil bro, Pavel Durov",
        "User Authorised.",
        "Calling Pavel Durov At +916969696969",
        "Private Call Connected...",
        "Me: Hello Sir, Please Ban This Telegram Account.",
        "Pavel Durov: May I Know Who is This?",
        f"Me: Yo Brah, I Am {kst.client.full_name}",
        "Pavel Durov: OMG!!! Long time no see, Wassup cat...\nI'll Make Sure That Guy Account Will Get Blocked Within 24Hrs.",
        "Me: Thanks, See You Later Brah.",
        "Pavel Durov: Please Don't Thank Brah, Telegram Is Our's. Just Gimme A Call When You Become Free.",
        "Me: Is There Any Issue/Emergency???",
        "Pavel Durov: Yes Sur, There is A Bug in Telegram v69.6.9.\nI Am Not Able To Fix It. If Possible, Please Help Fix The Bug.",
        "Me: Send Me The App On My Telegram Account, I Will Fix The Bug & Send You.",
        "Pavel Durov: Sure Sur \nTC Bye Bye :)",
        "Private Call Disconnected",
    )
    yy = await kst.eor("`Calling Pavel Durov (ceo of telegram)......`")
    for char in chars:
        await asyncio.sleep(3)
        await yy.eor(char, parse_mode=parse_pre)


@kasta_cmd(
    pattern="deploy$",
)
async def _(kst):
    chars = (
        "Heroku Connecting To Latest Github Build...",
        f"Build started by user {kst.client.full_name}",
        f"Deploy 515a69f0 by user {kst.client.full_name}",
        "Restarting Heroku Server...",
        "State changed from up to starting",
        "Stopping all processes with SIGTERM",
        "Process exited with status 143",
        "Starting process with command python3 -m getter",
        "State changed from starting to up",
        "INFO:Userbot:Logged in as 557697062",
        "INFO:Userbot:Successfully loaded all plugins",
        "Build Succeeded",
    )
    yy = await kst.eor("`Deploying...`")
    await asyncio.sleep(3)
    for char in chars:
        await asyncio.sleep(3)
        await yy.eor(char, parse_mode=parse_pre)


plugins_help["fun"] = {
    "{i}roll": "Roll a dice 1-7.",
    "{i}decide": "Randomly answers yes/no/maybe.",
    "{i}owo": "Get a random owo.",
    "{i}shg": "Get a random shrug.",
    "{i}ran": "Send random (⚽,🏀,🎳,🎲,🎯,🎰) emoji.",
    "{i}bol": "Send ⚽ emoji.",
    "{i}bas": "Send 🏀 emoji.",
    "{i}bow": "Send 🎳 emoji.",
    "{i}dic": "Send 🎲 emoji.",
    "{i}dar": "Send 🎯 emoji.",
    "{i}slot": "Send 🎰 emoji.",
    "{i}love|{i}fap|{i}star|{i}moon|{i}think|{i}lul|{i}clock|{i}muah|{i}gym|{i}earth|{i}candy|{i}rain|{i}run|{i}boxs": "Send a random flipping emoji.",
    "{i}heart": "Send a love emoji animation.",
    "{i}solars": "Solarsystem animation.",
    "{i}kocok": "Ngocok simulation.",
    "{i}dino": "Dino animation.",
    "{i}dick|{i}doggy|{i}dog|{i}fucku|{i}rose|{i}pki|{i}pistol|{i}ok": "Show the ascii art text by name.",
    "{i}baa|{i}bgst": "Some funny expressions.",
    "{i}thinking": "Thinking animation.",
    "{i}durov": "Call to durov.",
    "{i}deploy": "Deploy simulation.",
}
