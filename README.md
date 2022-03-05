# `getter`

> Get and put users (scraping) to the target **group/channel** efficiently, correctly and safety.

<p align="center">
    <a href="https://github.com/kastaid/getter/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/workflow/status/kastaid/getter/CI?logo=github&label=CI" /></a>
    <a href="https://app.codacy.com/gh/kastaid/getter/dashboard"><img alt="Codacy grade" src="https://img.shields.io/codacy/grade/2f86ed8f8534424c8d4cdaa197dc5ce2?logo=codacy" /></a>
    <a href="https://github.com/kastaid/getter/blob/main/LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/kastaid/getter" /></a>
    <a href="https://telegram.me/kastaid"><img alt="Telegram" src="https://img.shields.io/badge/kastaid-blue?logo=telegram" /></a>
    <br>
    <img alt="Version" src="https://img.shields.io/github/manifest-json/v/kastaid/getter" />
    <img alt="Size" src="https://img.shields.io/github/repo-size/kastaid/getter" />
    <a href="https://github.com/kastaid/getter/issues"><img alt="Issues" src="https://img.shields.io/github/issues/kastaid/getter" /></a>
    <a href="https://github.com/kastaid/getter/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/kastaid/getter" /></a>
    <a href="https://github.com/kastaid/getter/network/members"><img alt="Forks" src="https://img.shields.io/github/forks/kastaid/getter" /></a>
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
  - [Deploy](#deploy)
  - [Locally](#locally)
    - [Config](#config)
    - [Run](#run)
  - [Example Plugin](#example-plugin)
- [Credits](#credits)
- [Contributing](#contributing)
- [License](#license)

</details>

## Requirements

- Python 3.9.x
- Linux (Recommend Debian/Ubuntu)
- Telegram `API_ID` and `API_HASH` from [API development tools](my.telegram.org)

### STRING_SESSION

Generate `STRING_SESSION` using [@strgen_bot](https://telegram.me/strgen_bot) or [replit](https://replit.com/@notudope/strgen) or run locally `python3 session.py`

### Deploy

To deploy please visit our channel at [@kastaid](https://telegram.me/kastaid).

### Locally

#### Config

Create and save `config.env` file at main directory and fill with the example config file at [sample_config.env](https://github.com/kastaid/getter/blob/main/sample_config.env).

#### Run

```sh
# Production
pip3 install -r requirements.txt
python3 -m getter

# Development
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 -m run --watch
```

More commands `python3 -m run -h`

### Example Plugin

Clone the repo, then create and save plugin at `./getter/plugins/plugin_name.py`.

<kbd>This Example Works Everywhere. (e.g. Groups, Personal Chats)</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi")
async def hello_world_example(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Personal Chats.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda x: x.is_private)
async def hello_world_example(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Channels.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda x: x.is_channel and x.chat.broadcast)
async def hello_world_example(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Groups.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda x: x.is_group)
async def hello_world_example(event):
    await event.eor("Hello **World**.")
```

<kbd>This Example Works Only In Groups or Channels.</kbd>
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda x: not x.is_private)
async def hello_world_example(event):
    await event.eor("Hello **World**.")
```

## Credits

* [RaphielGang](https://github.com/RaphielGang) - Telegram-Paperplane
* [BianSepang](https://github.com/BianSepang) - WeebProject
* [userbotindo](https://github.com/userbotindo) - Userbot Indonesia Community
* [TeamUltroid](https://github.com/TeamUltroid) - Team Ultroid
* [mrismanaziz](https://github.com/mrismanaziz) - Man-Userbot

and [everyone](https://github.com/kastaid/getter/graphs/contributors) 🦄

## Contributing

If you would like to help out with some code, check the [details](https://github.com/kastaid/getter/blob/main/docs/CONTRIBUTING.md).

## License

This project is licensed under the [GNU Affero General Public License](https://github.com/kastaid/getter/blob/main/LICENSE) v3.0.
