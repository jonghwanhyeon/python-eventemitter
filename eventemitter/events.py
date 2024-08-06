from __future__ import annotations

from collections import OrderedDict
from typing import Generic, Hashable, TypeVar, Union

from eventemitter.collections import UserDict
from eventemitter.handlers import AbstractHandler, Handlers
from eventemitter.types import AsyncListenable, Listenable

L = TypeVar("L", bound=Union[Listenable, AsyncListenable])
H = TypeVar("H", bound=AbstractHandler)


class Events(UserDict[Hashable, Handlers[H]], Generic[L, H]):
    def __init__(self) -> None:
        self.data: OrderedDict[Hashable, Handlers[H]] = OrderedDict()

    def __getitem__(self, event: Hashable) -> Handlers[H]:
        if event not in self.data:
            self.data[event] = Handlers[H]()

        return self.data[event]

    def handlers(self, event: Hashable) -> list[H]:
        if event not in self.data:
            return []

        return list(self.data[event])

    def listeners(self, event: Hashable) -> list[L]:
        if event not in self.data:
            return []

        return [handler.func for handler in self.data[event]]
