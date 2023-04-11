from typing import Any

from eventemitter import core


class Executor(core.Executor[None]):
    def execute(self, handler: core.Handler[None], *args: Any, **kwargs: Any):
        handler(*args, **kwargs)


class EventEmitter(core.EventEmitter[None]):
    _executor_cls = Executor
