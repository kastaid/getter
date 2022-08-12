# getter < https://t.me/kastaid >
# Copyright (C) 2022 - kastaid
# All rights reserved.
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in;
# < https://www.github.com/kastaid/getter/blob/main/LICENSE/ >
# ================================================================

import json
from time import sleep
from . import Root


def main() -> None:
    try:
        for file in Root.rglob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                input = json.load(f)
            with open(file, "w", encoding="utf-8") as f:
                json.dump(
                    input,
                    f,
                    indent=4,
                    sort_keys=False,
                    ensure_ascii=False,
                )
                # outfile.write("\n")
                print(f"Pretty print : {file.name}")
            sleep(0.5)
    except BaseException:
        print(f"Failed to pretty print : {file}")
        raise


if __name__ == "__main__":
    main()
