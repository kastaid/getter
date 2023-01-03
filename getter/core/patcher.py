# getter < https://t.me/kastaid >
# Copyright (C) 2022-present kastaid
#
# This file is a part of < https://github.com/kastaid/getter/ >
# PLease read the GNU Affero General Public License in
# < https://github.com/kastaid/getter/blob/main/LICENSE/ >.

import typing
from functools import wraps


def patch(obj: typing.Any) -> typing.Callable:
    def is_patchable(item: typing.Tuple[str, typing.Any]) -> bool:
        return getattr(item[1], "patchable", False) or isinstance(item[1], property)

    @wraps(obj)
    def wrap(conta: typing.Any) -> typing.Any:
        for name, func in filter(is_patchable, conta.__dict__.items()):
            old = getattr(obj, name, None)
            setattr(obj, "old" + name, old)
            setattr(obj, name, func)
        return conta

    return wrap


def patchable(prop: bool = False) -> typing.Callable:
    def wrapp(func: typing.Any) -> typing.Union[typing.Callable, property]:
        func.patchable = True
        if prop:
            return property(func)
        return func

    return wrapp
