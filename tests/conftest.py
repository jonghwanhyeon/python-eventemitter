from __future__ import annotations

from typing import Any, Type

import pytest

from eventemitter import EventEmitter
from eventemitter.asyncio import AsyncIOEventEmitter


class Listeners:
    @staticmethod
    def foo():
        pass

    @staticmethod
    async def aio_foo():
        pass

    @staticmethod
    def bar():
        pass

    @staticmethod
    async def aio_bar():
        pass

    @staticmethod
    def baz():
        pass

    @staticmethod
    async def aio_baz():
        pass

    @staticmethod
    def add_item(container: list[Any], item: Any):
        container.append(item)

    @staticmethod
    async def aio_add_item(container: list[Any], item: Any):
        container.append(item)

    @staticmethod
    def add_item_twice(container: list[Any], item: Any):
        container.append(item)
        container.append(item)

    @staticmethod
    async def aio_add_item_twice(container: list[Any], item: Any):
        container.append(item)
        container.append(item)


@pytest.fixture
def ee() -> EventEmitter:
    return EventEmitter()


@pytest.fixture
def aio_ee() -> AsyncIOEventEmitter:
    return AsyncIOEventEmitter()


@pytest.fixture
def listeners() -> Type[Listeners]:
    return Listeners
