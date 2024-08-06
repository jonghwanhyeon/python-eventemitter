import asyncio
import functools
import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

from typing_extensions import ParamSpec, TypeGuard, overload

from eventemitter.types import AsyncCallable

T = TypeVar("T")

P = ParamSpec("P")
R = TypeVar("R")


# Reference: https://github.com/encode/starlette/blob/6f863b0d3b8e8f18d5df9e8cd2514f7085b874e1/starlette/_utils.py#L38
@overload
def is_coroutine_function(func: Callable[P, R]) -> TypeGuard[AsyncCallable[P, R]]: ...
@overload
def is_coroutine_function(func: AsyncCallable[P, R]) -> TypeGuard[AsyncCallable[P, R]]: ...


def is_coroutine_function(func: Any) -> Any:
    while isinstance(func, functools.partial):
        func = func.func

    return inspect.iscoroutinefunction(func) or (callable(func) and inspect.iscoroutinefunction(func.__call__))


@overload
def ensure_coroutine(func: Callable[P, R]) -> AsyncCallable[P, R]: ...
@overload
def ensure_coroutine(func: AsyncCallable[P, R]) -> AsyncCallable[P, R]: ...


def ensure_coroutine(func: Any) -> Any:
    if not callable(func):
        raise ValueError(f"Expected a callable but got {type(func)}")

    if is_coroutine_function(func):
        return func

    @functools.wraps(func)
    async def coroutine(*args: Any, **kwargs: Any) -> None:
        func(*args, **kwargs)

    return coroutine


def run_coroutine(coroutine: AsyncCallable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    def event_loop() -> R:
        loop = asyncio.new_event_loop()

        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coroutine(*args, **kwargs))
        finally:
            loop.close()

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(event_loop)
    return future.result()


def name_from_callable(func: Any) -> str:
    if not callable(func):
        raise ValueError(f"Expected a callable but got {type(func)}")

    if hasattr(func, "__name__"):
        return func.__name__
    elif hasattr(func, "__class__"):
        return type(func).__name__
    else:
        return repr(func)
