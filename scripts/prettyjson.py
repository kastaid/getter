# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

from glob import glob
from subprocess import check_call
from sys import executable
from time import sleep

try:
    import ujson as uj
except ModuleNotFoundError:
    print("Installing ujson...")
    check_call([executable, "-m", "pip", "install", "--no-cache-dir", "-U", "ujson==5.1.0"])
finally:
    import ujson as uj


def main() -> None:
    try:
        for json in glob("**/*.json", recursive=True):
            with open(json, "r", encoding="utf-8") as infile:
                file = uj.load(infile)
            with open(json, "w", encoding="utf-8") as outfile:
                uj.dump(
                    file,
                    outfile,
                    indent=4,
                    sort_keys=False,
                    ensure_ascii=False,
                    escape_forward_slashes=False,
                )
                # outfile.write("\n")
                print(f"Pretty print {json}")
            sleep(0.5)
    except BaseException:
        print(f"Failed to pretty print {json}")


if __name__ == "__main__":
    main()
