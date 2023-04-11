from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

from eventemitter.core.events import Handler

R = TypeVar("R")
C = Callable[..., R]


class Executor(Generic[R]):
    def execute(self, handler: Handler[R], *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError()
