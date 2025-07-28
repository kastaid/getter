# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

from json import dump, load

from . import Root

EXCLUDE = (".mypy_cache", "db")


def main() -> None:
    for p in filter(lambda x: not str(x.parent).endswith(EXCLUDE), Root.rglob("*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                data = load(f)
            with open(p, mode="w", encoding="utf-8") as f:
                dump(data, f, indent=4, sort_keys=False, ensure_ascii=False)
                print("Pretty print: ", p.name)
        except Exception as err:
            print("Failed to pretty print: ", str(err))


if __name__ == "__main__":
    raise SystemExit(main())
