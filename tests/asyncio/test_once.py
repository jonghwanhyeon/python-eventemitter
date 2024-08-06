from __future__ import annotations

from typing import Any

import pytest
from utils import fail, make_async_listener, trackable

from eventemitter import AsyncIOEventEmitter


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_once1(aee: AsyncIOEventEmitter) -> None:
    @aee.once("foo")
    async def on_foo(value: int) -> None:
        assert value == 42
        assert aee.listeners("foo") == []

    await aee.emit("foo", 42)


@pytest.mark.asyncio
async def test_once2(aee: AsyncIOEventEmitter) -> None:
    @aee.once("foo")
    async def on_foo(*values: int) -> None:
        assert values == (42, 24)

    await aee.emit("foo", 42, 24)


@pytest.mark.asyncio
async def test_once3(aee: AsyncIOEventEmitter) -> None:
    listener1 = trackable(make_async_listener())
    aee.once("hello", listener1)

    await aee.emit("hello", "a", "b")
    await aee.emit("hello", "a", "b")
    await aee.emit("hello", "a", "b")
    await aee.emit("hello", "a", "b")
    assert listener1.hits == 1

    aee.once("foo", fail)
    aee.remove_listener("foo", fail)
    await aee.emit("foo")

    @aee.once("bar")
    @trackable
    async def listener2(*args: Any, **kwargs: Any) -> None:
        await aee.emit("bar")

    @aee.once("bar")
    @trackable
    async def listener3(*args: Any, **kwargs: Any) -> None:
        pass

    await aee.emit_in_order("bar")
    assert listener2.hits == 1
    assert listener3.hits == 2


@pytest.mark.asyncio
async def test_once4() -> None:
    for i in range(5):
        aee = AsyncIOEventEmitter()
        parameters: list[str] = ["foo"]

        for j in range(0, i):
            parameters.append(str(j))

        @aee.once("foo")
        @trackable
        async def on_foo(*arguments: str) -> None:
            assert parameters[1:] == list(arguments)

        await aee.emit_in_order(*parameters)
        assert on_foo.hits == 1
