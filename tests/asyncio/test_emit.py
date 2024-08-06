from __future__ import annotations

from typing import Any

import pytest
from utils import make_async_listener, make_listener, trackable

from eventemitter import AsyncIOEventEmitter


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_emit(aee: AsyncIOEventEmitter) -> None:
    listener1 = trackable(make_async_listener())
    listener2 = trackable(make_async_listener())

    aee.on("foo", listener1)
    aee.on("bar", listener2)
    aee.on("bar", listener2)

    await aee.emit("foo")
    assert listener1.contexts[-1].num_args == 0

    await aee.emit("foo", None)
    assert listener1.contexts[-1].num_args == 1

    await aee.emit("foo", None, None)
    assert listener1.contexts[-1].num_args == 2

    await aee.emit("foo", None, None, None)
    assert listener1.contexts[-1].num_args == 3

    await aee.emit("foo", None, None, None, None)
    assert listener1.contexts[-1].num_args == 4

    await aee.emit("foo", None, None, None, None, None)
    assert listener1.contexts[-1].num_args == 5

    await aee.emit("bar", None, None, None, None)
    assert listener2.contexts[-1].num_args == 4
    assert listener2.contexts[-2].num_args == 4


@pytest.mark.asyncio
async def test_using_synchronous_listener(aee: AsyncIOEventEmitter) -> None:
    listener1 = trackable(make_listener())
    listener2 = trackable(make_listener())

    aee.on("foo", listener1)
    aee.on("bar", listener1)
    aee.on("bar", listener2)

    await aee.emit("foo")
    assert listener1.contexts[-1].num_args == 0
    assert listener1.hits == 1

    await aee.emit("foo", None)
    assert listener1.contexts[-1].num_args == 1
    assert listener1.hits == 2

    await aee.emit("bar")
    assert listener1.contexts[-1].num_args == 0
    assert listener1.hits == 3
    assert listener2.contexts[-1].num_args == 0
    assert listener2.hits == 1

    await aee.emit("bar", None)
    assert listener1.contexts[-1].num_args == 1
    assert listener1.hits == 4
    assert listener2.contexts[-1].num_args == 1
    assert listener2.hits == 2


@pytest.mark.asyncio
async def test_using_both_asynchronous_and_synchronous_listener(aee: AsyncIOEventEmitter) -> None:
    listener1 = trackable(make_async_listener())
    listener2 = trackable(make_listener())

    aee.on("foo", listener1)
    aee.on("bar", listener1)
    aee.on("bar", listener2)

    await aee.emit("foo")
    assert listener1.contexts[-1].num_args == 0
    assert listener1.hits == 1

    await aee.emit("foo", None)
    assert listener1.contexts[-1].num_args == 1
    assert listener1.hits == 2

    await aee.emit("bar")
    assert listener1.contexts[-1].num_args == 0
    assert listener1.hits == 3
    assert listener2.contexts[-1].num_args == 0
    assert listener2.hits == 1

    await aee.emit("bar", None)
    assert listener1.contexts[-1].num_args == 1
    assert listener1.hits == 4
    assert listener2.contexts[-1].num_args == 1
    assert listener2.hits == 2


@pytest.mark.asyncio
async def test_emit_concurrently(aee: AsyncIOEventEmitter) -> None:
    history: set[str] = set()

    @aee.on("foo")
    async def listener1(*args: Any, **kwargs: Any) -> None:
        history.add("listener1")

    @aee.on("foo")
    async def listener2(*args: Any, **kwargs: Any) -> None:
        history.add("listener2")

    @aee.on("foo")
    async def listener3(*args: Any, **kwargs: Any) -> None:
        history.add("listener3")

    @aee.on("foo")
    async def listener4(*args: Any, **kwargs: Any) -> None:
        history.add("listener4")

    @aee.on("foo")
    async def listener5(*args: Any, **kwargs: Any) -> None:
        history.add("listener5")

    await aee.emit("foo")
    assert history == {"listener1", "listener2", "listener3", "listener4", "listener5"}


@pytest.mark.asyncio
async def test_emit_in_order(aee: AsyncIOEventEmitter) -> None:
    history: list[str] = []

    @aee.on("foo")
    async def listener1(*args: Any, **kwargs: Any) -> None:
        history.append("listener1")

    @aee.on("foo")
    async def listener2(*args: Any, **kwargs: Any) -> None:
        history.append("listener2")

    @aee.on("foo")
    async def listener3(*args: Any, **kwargs: Any) -> None:
        history.append("listener3")

    @aee.on("foo")
    async def listener4(*args: Any, **kwargs: Any) -> None:
        history.append("listener4")

    @aee.on("foo")
    async def listener5(*args: Any, **kwargs: Any) -> None:
        history.append("listener5")

    await aee.emit_in_order("foo")
    assert history == ["listener1", "listener2", "listener3", "listener4", "listener5"]


@pytest.mark.asyncio
async def test_side_effect_of_emit1(aee: AsyncIOEventEmitter) -> None:
    history: set[str] = set()

    async def listener1(*args: Any, **kwargs: Any) -> None:
        history.add("listener1")
        aee.on("foo", listener2)
        aee.on("foo", listener3)
        aee.remove_listener("foo", listener1)

    async def listener2(*args: Any, **kwargs: Any) -> None:
        history.add("listener2")
        aee.remove_listener("foo", listener2)

    async def listener3(*args: Any, **kwargs: Any) -> None:
        history.add("listener3")
        aee.remove_listener("foo", listener3)

    aee.on("foo", listener1)
    assert aee.listeners("foo") == [listener1]

    await aee.emit("foo")
    assert aee.listeners("foo") == [listener2, listener3]
    assert history == {"listener1"}

    await aee.emit("foo")
    assert aee.listeners("foo") == []
    assert history == {"listener1", "listener2", "listener3"}

    await aee.emit("foo")
    assert aee.listeners("foo") == []
    assert history == {"listener1", "listener2", "listener3"}

    aee.on("foo", listener1)
    aee.on("foo", listener2)
    assert aee.listeners("foo") == [listener1, listener2]

    aee.remove_all_listeners("foo")
    assert aee.listeners("foo") == []


@pytest.mark.asyncio
async def test_side_effect_of_emit2(aee: AsyncIOEventEmitter) -> None:
    history: set[str] = set()

    async def listener1(*args: Any, **kwargs: Any) -> None:
        history.add("listener1")
        aee.remove_listener("foo", listener1)

    async def listener2(*args: Any, **kwargs: Any) -> None:
        history.add("listener2")
        aee.remove_listener("foo", listener2)

    aee.on("foo", listener1)
    aee.on("foo", listener2)
    assert aee.listeners("foo") == [listener1, listener2]

    await aee.emit("foo")
    assert history == {"listener1", "listener2"}
    assert aee.listeners("foo") == []
