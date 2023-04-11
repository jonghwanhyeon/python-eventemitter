import asyncio
from typing import Any, Awaitable, Union

from eventemitter import core


class AsyncIOExecutor(core.Executor[Union[Awaitable[None], None]]):
    def __init__(self):
        self._tasks: set[asyncio.Task[None]] = set()

    def execute(self, handler: core.Handler[Union[Awaitable[None], None]], *args: Any, **kwargs: Any):
        coroutine = handler(*args, **kwargs)
        if not asyncio.iscoroutine(coroutine):
            # handler is not coroutine function.
            # handler is already fired, thus do nothing.
            return

        # Invoke the handler in "fire-and-forget" fashion
        task = asyncio.create_task(coroutine)

        # Store a reference to the task to prevent it from disappearing mid-execution
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)


class AsyncIOEventEmitter(core.EventEmitter[Union[Awaitable[None], None]]):
    _executor_cls = AsyncIOExecutor
