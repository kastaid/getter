# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import os
import signal
import sys
from contextlib import suppress
from subprocess import CalledProcessError, Popen, check_call
from time import sleep
from typing import Generator
from . import (
    Root,
    EXTS,
    WAIT_FOR,
    RST,
    BOLD,
    RED,
    YELLOW,
)

try:
    import psutil as psu
except ModuleNotFoundError:
    print("Installing psutil...")
    check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-U", "psutil"])
finally:
    import psutil as psu


def file_times() -> Generator[int, None, None]:
    with suppress(BaseException):
        for f in filter(lambda p: p.suffix in EXTS, Root.rglob("*")):
            yield f.stat().st_mtime


def print_stdout(procs) -> None:
    out = procs.stdout
    if out:
        print(out)


def kill_process_tree(procs) -> None:
    with suppress(psu.NoSuchProcess):
        parent = psu.Process(procs.pid)
        child = parent.children(recursive=True)
        child.append(parent)
        for p in child:
            p.send_signal(signal.SIGTERM)
    procs.terminate()


def main() -> None:
    if len(sys.argv) <= 1:
        print("python3 -m scripts.autoreload [command]")
        sys.exit(0)
    cmd = " ".join(sys.argv[1:])
    procs = Popen(cmd, shell=True)
    last_mtime = max(file_times())
    try:
        while True:
            max_mtime = max(file_times())
            print_stdout(procs)
            if max_mtime > last_mtime:
                last_mtime = max_mtime
                print(f"{BOLD}{YELLOW}Restarting >> {procs.args}{RST}")
                kill_process_tree(procs)
                procs = Popen(cmd, shell=True)
            sleep(WAIT_FOR)
    except CalledProcessError as err:
        kill_process_tree(procs)
        sys.exit(err.returncode)
    except BaseException:
        print(f"{BOLD}{RED}Watch interrupted.{RST}")
    except KeyboardInterrupt:
        print(f"{BOLD}{RED}Kill process [{procs.pid}]{RST}")
        kill_process_tree(procs)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGINT)


if __name__ == "__main__":
    main()
