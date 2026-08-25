# Copyright (C) 2022-present kastaid
# https://github.com/kastaid/getter
# AGPL-3.0 License

from collections.abc import Callable
from contextlib import (
    asynccontextmanager,
    contextmanager,
)
from inspect import isasyncgenfunction
from typing import Any

type Decorator[T] = Callable[[type[T]], type[T]]
type AnyCallable = Callable[..., Any]


def patch[T](target: type[Any]) -> Decorator[T]:
    def wrapper(container: type[T]) -> type[T]:
        for name, func in container.__dict__.items():
            if not getattr(func, "patchable", False):
                continue

            old = getattr(target, name, None)
            if old is not None:
                setattr(target, f"old_{name}", old)

            if func.is_property:
                patched = property(func)
            elif func.is_static:
                patched = staticmethod(func)
            elif func.is_context:
                patched = asynccontextmanager(func) if isasyncgenfunction(func) else contextmanager(func)
            else:
                patched = func

            setattr(target, name, patched)

        return container

    return wrapper


def patchable(
    is_property: bool = False,
    is_static: bool = False,
    is_context: bool = False,
) -> Callable[[AnyCallable], AnyCallable]:
    def wrapper(func: AnyCallable) -> AnyCallable:
        func.patchable = True
        func.is_property = is_property
        func.is_static = is_static
        func.is_context = is_context
        return func

    return wrapper
