# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import sys
from contextlib import suppress
from os import getpid, kill
from pathlib import Path
from signal import (
    SIG_DFL,
    SIGINT,
    SIGTERM,
    signal,
)
from subprocess import CalledProcessError, Popen, check_call
from time import sleep
from typing import Generator

try:
    import psutil as psu
except ModuleNotFoundError:
    print("Installing psutil...")
    check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-U", "psutil"])
finally:
    import psutil as psu

RST = "\x1b[0m"
BOLD = "\x1b[1m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"

wait = 1
Root: Path = Path(__file__).parent.parent


def file_times() -> Generator[int, None, None]:
    ext = [".py", ".yml", ".env"]
    with suppress(BaseException):
        for f in filter(lambda p: p.suffix in ext, (Root).rglob("*")):
            yield f.stat().st_mtime


def print_stdout(process) -> None:
    stdout = process.stdout
    if stdout:
        print(stdout)


def kill_process_tree(process) -> None:
    with suppress(psu.NoSuchProcess):
        parent = psu.Process(process.pid)
        children = parent.children(recursive=True)
        children.append(parent)
        for p in children:
            p.send_signal(SIGTERM)
    process.terminate()


def main() -> None:
    if len(sys.argv) <= 1:
        print("python3 -m scripts.autoreload [command]")
        sys.exit(0)
    command = " ".join(sys.argv[1:])
    process = Popen(command, shell=True)
    last_mtime = max(file_times())
    try:
        while True:
            max_mtime = max(file_times())
            print_stdout(process)
            if max_mtime > last_mtime:
                last_mtime = max_mtime
                print(f"{BOLD}{YELLOW}Kill process [{process.pid}] and restarting [{process.args}]{RST}")
                kill_process_tree(process)
                process = Popen(command, shell=True)
            sleep(wait)
    except CalledProcessError as e:
        kill_process_tree(process)
        sys.exit(e.returncode)
    except BaseException:
        print("internal error!", file=sys.stderr)
        raise
    except KeyboardInterrupt:
        print(f"{BOLD}{RED}Kill process [{process.pid}]{RST}")
        kill_process_tree(process)
        signal(SIGINT, SIG_DFL)
        kill(getpid(), SIGINT)


if __name__ == "__main__":
    main()
