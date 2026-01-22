# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License


def get_version() -> str:
    import json

    with open("manifest.json") as f:
        data = json.load(f)
    return data.get("version", "unknown")


__version__ = get_version()
