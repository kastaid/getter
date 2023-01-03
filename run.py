# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import argparse
import shlex
import sys
from contextlib import suppress
from pathlib import Path
from subprocess import run
from version import __version__

RST = "\x1b[0m"
BOLD = "\x1b[1m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
CYAN = "\x1b[36m"

python = "python3"
nocache = f"{python} -B"
app = f"{python} -m getter"
app_watch = f"{python} -m scripts.autoreload {app}"

black = "black --line-length 120 --exclude version.py ."
isort = "isort --settings-file=setup.cfg ."
flake8 = "flake8 --config=setup.cfg ."
mypy = "mypy --config-file=setup.cfg ."
prettyjson = f"{nocache} -m scripts.prettyjson"


def run_cmd(cmd) -> None:
    try:
        proc = run(shlex.split(cmd), shell=False)
        if proc.returncode != 0:
            print(f"Exit code {proc.returncode}")
            sys.exit(1)
    except BaseException:
        sys.exit(1)


def clean() -> None:
    with suppress(BaseException):
        for _ in Path(".").rglob("*.py[co]"):
            _.unlink(missing_ok=True)
        for _ in Path(".").rglob("__pycache__"):
            _.rmdir()


def lint() -> None:
    print(f"{CYAN}>> {prettyjson}{RST}")
    run_cmd(prettyjson)
    print(f"{CYAN}>> {black}{RST}")
    run_cmd(black)
    print(f"{CYAN}>> {isort}{RST}")
    run_cmd(isort)
    print(f"{CYAN}>> {flake8}{RST}")
    run_cmd(flake8)


class CapitalisedHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if not prefix:
            prefix = "Usage: "
        return super(CapitalisedHelpFormatter, self).add_usage(usage, actions, groups, prefix)


parser = argparse.ArgumentParser(
    formatter_class=CapitalisedHelpFormatter,
    prog=f"{GREEN}{python} -m run{RST}",
    usage="%(prog)s [options]",
    epilog="Source code https://github.com/kastaid/getter",
    add_help=False,
)
parser._optionals.title = "Options"
parser.add_argument("-p", "--prod", help="run in production mode", action="store_true")
parser.add_argument("-d", "--dev", help="run in development mode", action="store_true")
parser.add_argument("-w", "--watch", help="run and watch in development mode", action="store_true")
parser.add_argument("-l", "--lint", help="run linting and format code", action="store_true")
parser.add_argument("-t", "--type", help="run type checker only", action="store_true")
parser.add_argument("-c", "--clean", help="remove python caches", action="store_true")
parser.add_argument(
    "-v",
    "--version",
    help="show this program version",
    action="version",
    version=__version__,
)
parser.add_argument(
    "-h",
    "--help",
    help="show this help information",
    default=argparse.SUPPRESS,
    action="help",
)


def main() -> None:
    args = parser.parse_args()
    if args.prod:
        print(f"{BOLD}{GREEN}PRODUCTION MODE...{RST}")
        clean()
        print(f"{BOLD}{BLUE}>> {app}{RST}")
        run_cmd(app)
    elif args.dev:
        print(f"{BOLD}{GREEN}DEVELOPMENT MODE...{RST}")
        clean()
        lint()
        print(f"{BOLD}{BLUE}>> {app}{RST}")
        run_cmd(app)
    elif args.watch:
        print(f"{BOLD}{GREEN}WATCHED DEVELOPMENT MODE...{RST}")
        clean()
        print(f"{BOLD}{BLUE}>> {app_watch}{RST}")
        run_cmd(app_watch)
    elif args.lint:
        print(f"{BOLD}{YELLOW}Run linting and format code...{RST}")
        clean()
        lint()
    elif args.type:
        print(f"{BOLD}{YELLOW}Run type checker...{RST}")
        clean()
        run_cmd(mypy)
    elif args.clean:
        clean()
    else:
        print(f"{python} -m run --help")


if __name__ == "__main__":
    main()
