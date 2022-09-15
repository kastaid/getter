# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import json
import sys
import time
from . import Root


def main() -> None:
    try:
        for file in filter(lambda p: ".mypy_cache" not in set(str(p.parent).split("/")), Root.rglob("*.json")):
            with open(file, "r", encoding="utf-8") as fp:
                obj = json.load(fp)
            with open(file, "w", encoding="utf-8") as fp:
                json.dump(
                    obj,
                    fp,
                    indent=4,
                    sort_keys=False,
                    ensure_ascii=False,
                )
                # outfile.write("\n")
                print(f"Pretty print : {file.name}")
            time.sleep(0.3)
    except BaseException:
        print(f"Failed to pretty print : {file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
