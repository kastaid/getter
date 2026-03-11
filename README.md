# getter

**A powerful and customizable Telegram userbot built with Telethon. Create custom plugins, automate tasks, and enhance your Telegram experience.**

[![CI](https://github.com/kastaid/getter/workflows/CI/badge.svg)](https://github.com/kastaid/getter/actions/workflows/ci.yml)
[![LICENSE](https://img.shields.io/github/license/kastaid/getter)](LICENSE)
![Version](https://img.shields.io/github/manifest-json/v/kastaid/getter?label=Version)

> [!WARNING]
> Your Telegram account may get banned if this userbot is misused. We are not responsible for any spam, violations, or account restrictions.
>
> Use it at your own risk and review the [Telegram API Terms](https://core.telegram.org/api/terms).

## Table of Contents

- [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [Clone Repository](#clone-repository)
    - [String Session](#string-session)
    - [Config](#config)
- [Deployments](#deployments)
  - [Docker Compose](#docker-compose)
    - [Full version](#full-version)
    - [Lite version](#lite-version)
  - [Locally](#locally)
  - [Heroku](#heroku)
- [Usage](#usage)
- [Custom Plugins](#custom-plugins)
- [Supports](#supports)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.13+
- Linux (Debian/Ubuntu)
- Telegram `API_ID` and `API_HASH` from [API development tools](https://my.telegram.org)

## Quick Start

Follow these steps to set up and run **getter** on your system.

### Clone Repository

```sh
git clone https://github.com/kastaid/getter.git
cd getter
```

#### String Session

Generate `STRING_SESSION` by choosing **Telethon** at [@strgen_bot](https://t.me/strgen_bot) or run `python3 strgen.py`.

#### Config

Create a `.env` file in the main directory and fill it with the example from [example.env](example.env).

## Deployments

Choose your preferred deployment method below.

### Docker Compose

Deploy using Docker Compose for easy containerized deployment.

#### Full version
```sh
git pull && \
  docker compose -f full-compose.yml up -d --build && \
  docker compose -f full-compose.yml logs -f
```

#### Lite version
```sh
git pull && \
  docker compose -f lite-compose.yml up -d --build && \
  docker compose -f lite-compose.yml logs -f
```

### Locally

Run getter locally on your machine or server (e.g., on Termux).

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

Deploy to Heroku with one click:

[![Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/kastaid/getter)

## Usage

Once successfully deployed, test your getter by sending `.ping` in any chat.

**Command prefix**:

- Default prefix is `.` (dot)
- If you set a custom `HANDLER` in your [config](#config), use that prefix instead (e.g., `!ping`, `/ping`)
- If `NO_HANDLER` is set to `True`, send commands without any prefix (e.g., `ping`)

**Get all commands**: `.help` - This will show you all available plugins, commands, and how to use them.

## Custom Plugins

Create custom plugins at `./getter/plugins/custom/plugin_name.py`.

**Dynamic plugin management**:

- Upload your `plugin_name.py` file anywhere in Telegram (plugin name must be unique)
- Reply to the file with `.load` to download, activate, or update the plugin
- Reply to the plugin file with `.unload [plugin_name]` to remove it

**Example plugin**:

```python
from . import kasta_cmd

# Works everywhere (e.g., groups, personal chats)
@kasta_cmd(pattern="hi")
async def _(event):
    await event.eor("Hello **World**")

# Works only in personal chats
@kasta_cmd(pattern="hi", func=lambda e: e.is_private)
async def _(event):
    await event.eor("Hello **World**")

# Works only in channels
@kasta_cmd(pattern="hi", func=lambda e: e.is_channel and e.chat.broadcast)
async def _(event):
    await event.eor("Hello **World**")

# Works only in groups
@kasta_cmd(pattern="hi", func=lambda e: e.is_group)
async def _(event):
    await event.eor("Hello **World**")

# Works only in groups or channels
@kasta_cmd(pattern="hi", func=lambda e: not e.is_private)
async def _(event):
    await event.eor("Hello **World**")
```

For available modules, imports, functions, and methods, see [`__init__.py`](getter/plugins/__init__.py).

## Supports

If you’re enjoying it or want to support development, feel free to donate. Thank you! ❤️

## Contributing

Want to contribute? Read the [Contributing](docs/CONTRIBUTING.md).

## License

Released under the [AGPL-3.0 License](LICENSE).
