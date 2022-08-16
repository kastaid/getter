# getter < https://t.me/kastaid >
# Copyright (C) 2022 kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

def get_version() -> str:
    import json
    with open("manifest.json", mode="r") as f:
        data = json.load(f)
    return data["version"] or "unknown"
__version__ = get_version()
