# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import os
import signal
import sys
import time
from subprocess import CalledProcessError, Popen, check_call
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
    import psutil
except ModuleNotFoundError:
    print("Installing psutil...")
    check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-U", "psutil"])
finally:
    import psutil


def file_times() -> Generator[int, None, None]:
    for _ in filter(lambda p: p.suffix in EXTS, Root.rglob("*")):
        yield _.stat().st_mtime


def print_stdout(procs) -> None:
    out = procs.stdout
    if out:
        print(out)


def kill_process_tree(procs) -> None:
    try:
        parent = psutil.Process(procs.pid)
        child = parent.children(recursive=True)
        child.append(parent)
        for _ in child:
            _.send_signal(signal.SIGTERM)
    except psutil.NoSuchProcess:
        pass
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
            time.sleep(WAIT_FOR)
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
