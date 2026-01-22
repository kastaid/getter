# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from collections.abc import Callable
from functools import wraps
from typing import Any, T


def patch(target: Any):
    def is_patchable(item: tuple[str, Any]) -> bool:
        return getattr(item[1], "patchable", False)

    @wraps(target)
    def wrapper(container: type[T]) -> T:
        for name, func in filter(is_patchable, container.__dict__.items()):
            old = getattr(target, name, None)
            if old is not None:
                setattr(target, f"old_{name}", old)
            if getattr(func, "is_property", False):
                func = property(func)
            setattr(target, name, func)
        return container

    return wrapper


def patchable(is_property: bool = False) -> Callable:
    def wrapper(func: Callable) -> Callable:
        func.patchable = True
        func.is_property = is_property
        return func

    return wrapper
