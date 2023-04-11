from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from eventemitter.utils import rindex

R = TypeVar("R")
C = Callable[..., R]


@dataclass(eq=False)
class Handler(Generic[R]):
    id: int
    func: C[R]
    once: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> R:
        return self.func(*args, **kwargs)


class Events(Generic[R]):
    def __init__(self):
        self._handlers: dict[str, list[Handler[R]]] = defaultdict(list)

    def add_handler(self, event: str, handler: Handler[R]):
        self._handlers[event].append(handler)

    def remove_handler(self, event: str, handler: Handler[R]):
        index = self._handlers[event].index(handler)
        self._remove_handler_at(event, index)

    def remove_handler_by_id(self, event: str, id: int):
        # According to the official node.js document:
        # > When a single function has been added as a handler multiple times for a single event,
        # > removeListener() will remove the most recently added instance
        index = rindex([handler.id for handler in self._handlers[event]], id)
        self._remove_handler_at(event, index)

    def names(self) -> list[str]:
        return list(self._handlers.keys())

    def handlers(self, event: str) -> list[Handler[R]]:
        if event not in self._handlers:
            raise ValueError(f"event {event} does not exist")

        return list(self._handlers[event])

    def clear(self):
        self._handlers.clear()

    def _remove_handler_at(self, event: str, index: int):
        del self._handlers[event][index]

        if not self._handlers[event]:
            del self._handlers[event]

    def __getitem__(self, event: str):
        return self._handlers[event]

    def __delitem__(self, event: str):
        del self._handlers[event]

    def __contains__(self, event: str):
        return event in self._handlers
