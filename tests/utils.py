from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar, Union

from typing_extensions import overload

from eventemitter.types import AsyncListenable, Listenable
from eventemitter.utils import is_coroutine_function, name_from_callable

L = TypeVar("L", bound=Union[Listenable, AsyncListenable])


@dataclass(frozen=True)
class Context:
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    @property
    def num_args(self) -> int:
        return len(self.args) + len(self.kwargs)


@dataclass
class AbstractTrackable(ABC, Generic[L]):
    listener: L
    contexts: list[Context] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.__name__ = name_from_callable(self.listener)

    @property
    def hits(self) -> int:
        return len(self.contexts)

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class Trackable(AbstractTrackable[Listenable], Listenable):
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.contexts.append(Context(args=args, kwargs=kwargs))
        self.listener(*args, **kwargs)

    __hash__ = AbstractTrackable.__hash__


@dataclass
class AsyncTrackable(AbstractTrackable[AsyncListenable], AsyncListenable):
    async def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.contexts.append(Context(args=args, kwargs=kwargs))
        await self.listener(*args, **kwargs)

    __hash__ = AbstractTrackable.__hash__


def success(*args: Any, **kwargs: Any) -> None:
    assert True


def fail(*args: Any, **kwargs: Any) -> None:
    assert False


@overload
def trackable(listener: Listenable) -> Trackable: ...
@overload
def trackable(listener: AsyncListenable) -> AsyncTrackable: ...


def trackable(listener: Any) -> Any:
    if is_coroutine_function(listener):
        return AsyncTrackable(listener)
    else:
        return Trackable(listener)


def make_listener(func: Optional[Listenable] = None) -> Listenable:
    def listener(*args: Any, **kwargs: Any) -> None:
        if func is not None:
            func(*args, **kwargs)

    return listener


def make_async_listener(func: Optional[Listenable] = None) -> AsyncListenable:
    async def async_listener(*args: Any, **kwargs: Any) -> None:
        if func is not None:
            func(*args, **kwargs)

    return async_listener
