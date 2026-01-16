# getter

**Powerful Telethon userbot (supports custom plugins)**

[![CI](https://github.com/kastaid/getter/workflows/CI/badge.svg)](https://github.com/kastaid/getter/actions/workflows/ci.yml)
[![LICENSE](https://img.shields.io/github/license/kastaid/getter)](LICENSE)
![Version](https://img.shields.io/github/manifest-json/v/kastaid/getter?label=Version)

## Disclaimer

**Important:** Your Telegram account may get banned. We are not responsible for any misuse of this userbot.

If you spam, face issues with Telegram, or get your account deleted, **DON’T BLAME US!**
- No personal support.
- We won’t spoon-feed you.
- If you need help with this userbot, ask in our support group, and we or others will try to help you.

Please review the **[Telegram API Terms of Service](https://core.telegram.org/api/terms)**.

Thank you for trusting and using this userbot!

## Table of Contents

- [Requirements](#requirements)
  - [STRING_SESSION](#string_session)
  - [Config](#config)
- [Deployments](#deployments)
  - [Docker Compose](#docker-compose)
    - [Full version](#full-version)
    - [Lite version](#lite-version)
  - [Locally](#locally)
  - [Heroku](#heroku)
- [Example Plugin](#example-plugin)
- [Supports](#supports)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.11.x
- Linux (Recommend Debian/Ubuntu)
- Telegram `API_ID` and `API_HASH` from [API development tools](https://my.telegram.org)

### STRING_SESSION

Generate `STRING_SESSION` using [@strgen_bot](https://t.me/strgen_bot) or run locally `python3 strgen.py`

### Config

Create a `.env` file in the main directory and fill it with the example from [example.env](example.env).

## Deployments

Deploy getter locally or on your server.

### Docker Compose

Deploy using Docker Compose.

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

Run getter locally (e.g., on Termux).

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

More commands: run `python3 -m run -h`.

### Heroku

One-click deploy: [![Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/kastaid/getter)

## Example Plugin

Clone this repo and create a plugin at `./getter/plugins/plugin_name.py`.

Works everywhere (e.g., groups, personal chats):
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi")
async def _(event):
    await event.eor("Hello **World**")
```

Works only in personal chats:
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: e.is_private)
async def _(event):
    await event.eor("Hello **World**")
```

Works only in channels:
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: e.is_channel and e.chat.broadcast)
async def _(event):
    await event.eor("Hello **World**")
```

Works only in groups:
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: e.is_group)
async def _(event):
    await event.eor("Hello **World**")
```

Works only in groups or channels:
```python
from . import kasta_cmd
@kasta_cmd(pattern="hi", func=lambda e: not e.is_private)
async def _(event):
    await event.eor("Hello **World**")
```

## Supports

If you’re enjoying it or want to support development, feel free to donate. Thank you! ❤️

## Contributing

Want to contribute? Read the [Contributing](docs/CONTRIBUTING.md).

## License

Released under the [AGPL-3.0 License](LICENSE).
