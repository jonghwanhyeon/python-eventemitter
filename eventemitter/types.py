import sys
from typing import Any, Callable, Coroutine, TypeVar, Union

from typing_extensions import ParamSpec

T = TypeVar("T")

P = ParamSpec("P")
R = TypeVar("R")

if sys.version_info >= (3, 10):
    AsyncCallable = Callable[P, Coroutine[Any, Any, R]]

    Listenable = Callable[..., None]
    AsyncListenable = AsyncCallable[..., None]
else:
    AsyncCallable = Callable[P, Coroutine[Any, Any, R]]

    Listenable = Callable[..., None]
    AsyncListenable = Callable[..., Coroutine[Any, Any, None]]

Returns = Union[T, Coroutine[Any, Any, T]]
