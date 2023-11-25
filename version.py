# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

def get_version() -> str:
    import json
    with open("manifest.json", mode="r") as fp:
        data = json.load(fp)
    return data.get("version", "unknown")
__version__ = get_version()
