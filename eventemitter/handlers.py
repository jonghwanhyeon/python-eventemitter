import sys
from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union

from typing_extensions import Self, assert_never

from eventemitter.collections import UserList
from eventemitter.types import AsyncListenable, Listenable
from eventemitter.utils import ensure_coroutine, name_from_callable

L = TypeVar("L", bound=Union[Listenable, AsyncListenable])
H = TypeVar("H", bound="AbstractHandler")

_dataclass_options = {}
if sys.version_info >= (3, 10):
    _dataclass_options["slots"] = True


@dataclass(frozen=True, **_dataclass_options)
class AbstractHandler(ABC, Generic[L]):
    id: int
    func: L
    once: bool

    @classmethod
    def from_func(cls: Type[Self], func: L, once: bool = False) -> Self:
        return cls(id=id(func), func=func, once=once)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(func={name_from_callable(self.func)}@0x{self.id:x}, once={self.once!r})"


@dataclass(frozen=True, **_dataclass_options)
class Handler(AbstractHandler[Listenable]):
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.func(*args, **kwargs)


@dataclass(frozen=True, **_dataclass_options)
class AsyncHandler(AbstractHandler[Union[Listenable, AsyncListenable]]):
    coroutine: AsyncListenable

    @classmethod
    def from_func(cls: Type[Self], func: Union[Listenable, AsyncListenable], once: bool = False) -> Self:
        return cls(id=id(func), func=func, once=once, coroutine=ensure_coroutine(func))

    async def __call__(self, *args: Any, **kwargs: Any) -> None:
        await self.coroutine(*args, **kwargs)


class Handlers(UserList[H], Generic[H]):
    def prepend(self, handler: H) -> None:
        self.data.insert(0, handler)

    def find(self, target: H) -> Optional[int]:
        return self._find(lambda handler: handler is target)

    def find_by_id(self, target: Union[H, Listenable, AsyncListenable]) -> Optional[int]:
        target_id = self._id_of(target)
        return self._find(lambda handler: handler.id == target_id)

    def rfind(self, target: H) -> Optional[int]:
        return self._rfind(lambda handler: handler is target)

    def rfind_by_id(self, target: Union[H, Listenable, AsyncListenable]) -> Optional[int]:
        target_id = self._id_of(target)
        return self._rfind(lambda handler: handler.id == target_id)

    def remove(self, target: H, last: bool = False) -> H:  # type: ignore[override]
        finder = self.find if not last else self.rfind
        index = finder(target)

        if index is None:
            raise ValueError(f"{target!r} not in list")

        return self.data.pop(index)

    def remove_by_id(self, target: Union[H, Listenable, AsyncListenable], last: bool = False) -> H:
        finder = self.find_by_id if not last else self.rfind_by_id
        index = finder(target)

        if index is None:
            raise ValueError(f"{target!r} not in list")

        return self.data.pop(index)

    def _find(self, condition: Callable[[H], bool]) -> Optional[int]:
        for index, handler in enumerate(self.data):
            if condition(handler):
                return index
        else:
            return None

    def _rfind(self, condition: Callable[[H], bool]) -> Optional[int]:
        for index, handler in enumerate(reversed(self.data)):
            if condition(handler):
                return len(self.data) - index - 1
        else:
            return None

    @staticmethod
    def _id_of(instance: Union[H, Listenable, AsyncListenable]) -> int:
        if isinstance(instance, AbstractHandler):
            return instance.id
        elif callable(instance):
            return id(instance)
        else:
            assert_never(instance)
