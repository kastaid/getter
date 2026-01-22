# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from random import choice

from telethon.tl.custom.inlineresult import InlineResult

from . import (
    LANG_CODES,
    Fetch,
    formatx_send,
    import_lib,
    kasta_cmd,
    plugins_help,
)

BOT_INLINE = "@gamee"
BOT_TICTAC = "@xobot"


@kasta_cmd(
    pattern="listgame$",
)
async def _(kst):
    yy = await kst.eor("`Getting games...`")
    try:
        chat = await kst.get_input_chat()
        res = await kst.client.inline_query(
            BOT_INLINE,
            query="",
            entity=chat,
        )
        games = [getattr(_, "title", "") for _ in res if isinstance(_, InlineResult)]
        text = f"**{len(games)} Games:**\n" + "\n".join([f"- `{_}`" for _ in games])
        text += "\n\n__Choose one, tap or copy, then put to 'game' command!__"
        await yy.eor(text, parts=True)
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="game(?: |$)(.*)",
)
async def _(kst):
    query = await kst.client.get_text(kst)
    yy = await kst.eor("`Playing game...`")
    try:
        chat = await kst.get_input_chat()
        res = await kst.client.inline_query(
            BOT_INLINE,
            query=query,
            entity=chat,
        )
        play = None
        games = [_ for _ in res if isinstance(_, InlineResult)]
        if query:
            for game in games:
                if getattr(game, "title", "").lower() == query.lower():
                    play = game
                    break
            if not play:
                play = res[0]
        else:
            play = choice(games)
        await play.click(
            reply_to=kst.reply_to_msg_id,
            silent=True,
        )
        await yy.try_delete()
    except IndexError:
        await yy.eod(f"**No Results for:** `{query}`")
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="xo$",
)
async def _(kst):
    query = "play"
    yy = await kst.eor("`Playing game...`")
    try:
        chat = await kst.get_input_chat()
        res = await kst.client.inline_query(
            BOT_TICTAC,
            query=query,
            entity=chat,
        )
        await res[0].click(reply_to=kst.reply_to_msg_id)
        await yy.try_delete()
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


@kasta_cmd(
    pattern="(truth|dare)(?: |$)(.*)",
)
async def _(kst):
    group = kst.pattern_match.group
    cmd, lang, lang_code, text = group(1), group(2), None, ""
    yy = await kst.eor("`Getting question...`")
    if lang in LANG_CODES:
        lang_code = lang
    if cmd == "truth":
        url = "https://api.truthordarebot.xyz/v1/truth"
        text += "<b><u>Truth</u></b>\n"
    else:
        url = "https://api.truthordarebot.xyz/v1/dare"
        text += "<b><u>Dare</u></b>\n"
    res = await Fetch(url, re_json=True)
    if not res:
        return await yy.eod("`Try again now!`")
    try:
        from gpytranslate import Translator
    except ImportError:
        Translator = import_lib(
            lib_name="gpytranslate",
            pkg_name="gpytranslate==1.5.1",
        ).Translator
    try:
        tod = str(res.get("question"))
        if lang_code:
            tod = (await Translator()(tod, targetlang=lang_code)).text
        text += tod
        await yy.sod(text, parse_mode="html")
    except Exception as err:
        await yy.eor(formatx_send(err), parse_mode="html")


plugins_help["games"] = {
    "{i}listgame": "List all game name.",
    "{i}game [game_name]": "Play an inline games by `@gamee`. Add 'game_name' or leave blank to get random games. E.g: `{i}game Karate Kido`",
    "{i}xo": "Play the Tic Tac Toe game.",
    "{i}truth [lang_code]": "Get a random truth task. Add 'lang_code' to translate question. E.g: `{i}truth id`",
    "{i}dare [lang_code]": "Get a random dare task.",
}
