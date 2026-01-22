# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

import signal
import sys
from os import getpid, kill
from subprocess import CalledProcessError, Popen, check_call
from time import sleep

from . import (
    BOLD,
    EXTS,
    RED,
    RST,
    WAIT_FOR,
    YELLOW,
    Root,
)

try:
    import psutil
except ModuleNotFoundError:
    print("Installing psutil...")
    check_call([sys.executable, "-m", "pip", "install", "-U", "psutil"])
finally:
    import psutil


def file_time() -> float:
    return max(f.stat().st_mtime for f in Root.rglob("*") if f.suffix in EXTS)


def print_stdout(procs) -> None:
    out = procs.stdout
    if out:
        print(out)


def kill_process_tree(procs) -> None:
    try:
        parent = psutil.Process(procs.pid)
        child = parent.children(recursive=True)
        child.append(parent)
        for c in child:
            c.send_signal(signal.SIGTERM)
    except psutil.NoSuchProcess:
        pass
    procs.terminate()


def main() -> None:
    if len(sys.argv) <= 1:
        print("python3 -m scripts.autoreload [command]")
        sys.exit(0)
    cmd = " ".join(sys.argv[1:])
    procs = Popen(cmd, shell=True)
    last_mtime = file_time()
    try:
        while True:
            max_mtime = file_time()
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
    except KeyboardInterrupt:
        print(f"{BOLD}{RED}Kill process [{procs.pid}]{RST}")
        kill_process_tree(procs)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        kill(getpid(), signal.SIGINT)
    except BaseException:
        print(f"{BOLD}{RED}Watch interrupted.{RST}")


if __name__ == "__main__":
    raise SystemExit(main())
