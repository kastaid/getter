# `getter`

> Get and put users (scraping) to the target **group/channel** efficiently, correctly and safety.

<p align="center">
    <a href="https://github.com/kastaid/getter/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/kastaid/getter/ci.yml?branch=main&logo=github&label=CI" /></a>
    <img alt="Python" src="https://img.shields.io/badge/Python-3.11.x%20%7C%203.12.x-blue?logoColor=white&logo=python" />
    <img alt="Version" src="https://img.shields.io/github/manifest-json/v/kastaid/getter" />
    <a href="https://github.com/kastaid/getter/blob/main/LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/kastaid/getter" /></a>
    <a href="https://telegram.me/kastaid"><img alt="Telegram" src="https://img.shields.io/badge/kastaid-blue?logo=telegram" /></a>
</p>

```
#include <std/disclaimer.h>
/*
*   Your Telegram account may get banned.
*   We are not responsible for any improper use of this userbot.
*   This userbot is specific for scraping members with some helpfull commands.
*
*   If you ended up spamming groups, getting reported left and right,
*   and you ended up in being fight with Telegram
*   and at the end Telegram Team deleted your account. DON'T BLAME US.
*
*   No personal support will be provided / We won't spoon feed you.
*   If you need help ask in our support group 
*   and we or our friends will try to help you.
*/
```

## Table of Contents

<details>
<summary>Details</summary>

- [Requirements](#requirements)
  - [STRING_SESSION](#string_session)
  - [Config](#config)
- [Deployments](#deployments)
  - [Docker Compose](#docker-compose)
    - [Full version](#full-version)
    - [Lite version](#lite-version)
  - [Locally](#locally)
- [Example Plugin](#example-plugin)
- [Supports](#sparkling_heart-supports)
- [Credits and Thanks](#credits-and-thanks)
- [Contributing](#contributing)
- [License](#license)

</details>

## Requirements

- Python 3.11.x
- Linux (Recommend Debian/Ubuntu)
- Telegram `API_ID` and `API_HASH` from [API development tools](https://my.telegram.org)

### STRING_SESSION

Generate `STRING_SESSION` using [@strgen_bot](https://telegram.me/strgen_bot) or [replit](https://replit.com/@notudope/strgen) or run locally `python3 strgen.py`

### Config

Create and save `config.env` file at main directory and fill with the example config file at [sample_config.env](https://github.com/kastaid/getter/blob/main/sample_config.env).

## Deployments

Deploy getter to your server or locally.

### Docker Compose

Deploy to your server using docker compose.

#### Full version
```sh
git pull && \
  docker compose -f full-compose.yml up --detach --build --force-recreate && \
  docker compose -f full-compose.yml logs -f
```

#### Lite version
```sh
git pull && \
  docker compose -f lite-compose.yml up --detach --build --force-recreate && \
  docker compose -f lite-compose.yml logs -f
```

### Locally

Run getter as locally eg: termux

#### Production
```sh
pip3 install -r requirements.txt
python3 -m getter
```

#### Development
```sh
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 -m run --watch
```

More commands `python3 -m run -h`

## Example Plugin

Clone the repo, then create and save plugin at `./getter/plugins/plugin_name.py`.

<kbd>This Example Works Everywhere. (e.g. Groups, Personal Chats)</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi")
async def _(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Personal Chats.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: e.is_private)
async def _(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Channels.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: e.is_channel and e.chat.broadcast)
async def _(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Groups.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: e.is_group)
async def _(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Groups or Channels.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: not e.is_private)
async def _(event):
    await event.eor("Hello **World**.")
```

## :sparkling_heart: Supports

This project is open source and free to use under the [license](#license). However, if you are using this project and happy with it or just want to encourage me to continue creating stuff please donate!

## Credits and Thanks

* [LonamiWebs](https://github.com/LonamiWebs/Telethon) - Telethon
* [TeamUltroid](https://github.com/TeamUltroid) - Team Ultroid
* [userbotindo](https://github.com/userbotindo) - Userbot Indonesia Community
* [illvart](https://github.com/illvart) - Core Developer

and [everyone](https://github.com/kastaid/getter/graphs/contributors) 🦄

## Contributing

If you would like to help out with some code, check the [details](https://github.com/kastaid/getter/blob/main/docs/CONTRIBUTING.md).

## License

This project is licensed under the **GNU Affero General Public License v3.0**. See the [LICENSE](https://github.com/kastaid/getter/blob/main/LICENSE) file for details.
