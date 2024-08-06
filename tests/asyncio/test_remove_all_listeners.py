from __future__ import annotations

import pytest
from utils import fail, make_async_listener, trackable

from eventemitter import AsyncIOEventEmitter
from eventemitter.types import AsyncListenable


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_remove_all_listeners1(aee: AsyncIOEventEmitter) -> None:
    listener = make_async_listener()

    aee.on("foo", listener)
    aee.on("bar", listener)
    aee.on("baz", listener)
    aee.on("baz", listener)

    foo_listeners = aee.listeners("foo")
    bar_listeners = aee.listeners("bar")
    baz_listeners = aee.listeners("baz")

    removed_events: list[str] = []

    @aee.on("remove_listener")
    async def on_removed(event: str, listener: AsyncListenable) -> None:
        removed_events.append(event)

    aee.remove_all_listeners("bar")
    aee.remove_all_listeners("baz")

    assert removed_events == ["bar", "baz", "baz"]
    assert aee.listeners("bar") == []
    assert aee.listeners("baz") == []

    # After calling remove_all_listeners(), the old listeners list should stay unchanged
    assert foo_listeners == [listener]
    assert bar_listeners == [listener]
    assert baz_listeners == [listener, listener]

    # After calling remove_all_listeners(), new listeners list is different from the old
    assert aee.listeners("bar") != bar_listeners
    assert aee.listeners("baz") != baz_listeners


@pytest.mark.asyncio
async def test_remove_all_listeners2(aee: AsyncIOEventEmitter) -> None:
    aee.on("foo", fail)
    aee.on("bar", fail)

    listener1 = trackable(make_async_listener())
    listener2 = trackable(make_async_listener())

    aee.on("remove_listener", listener1)
    aee.on("remove_listener", listener2)
    aee.remove_all_listeners()

    # Expect LIFO order
    assert [context.args[0] for context in listener1.contexts] == ["foo", "bar", "remove_listener"]
    assert [context.args[0] for context in listener2.contexts] == ["foo", "bar"]


@pytest.mark.asyncio
async def test_remove_all_listeners3(aee: AsyncIOEventEmitter) -> None:
    aee.on("remove_listener", fail)
    try:
        aee.remove_all_listeners("foo")
    except Exception:
        assert False


@pytest.mark.asyncio
async def test_remove_all_listeners4(aee: AsyncIOEventEmitter) -> None:
    expected = 2

    @aee.on("remove_listener")
    async def on_remove_listener(event: str, listener: AsyncListenable) -> None:
        nonlocal expected
        assert aee.listeners("baz") == [listener1, listener2][:expected]
        expected -= 1

    listener1 = make_async_listener(fail)
    listener2 = make_async_listener(fail)
    listener3 = make_async_listener(fail)

    aee.on("baz", listener1)
    aee.on("baz", listener2)
    aee.on("baz", listener3)
    assert aee.listeners("baz") == [listener1, listener2, listener3]

    aee.remove_all_listeners("baz")
    assert aee.listeners("baz") == []


@pytest.mark.asyncio
async def test_remove_all_listeners5(aee: AsyncIOEventEmitter) -> None:
    assert aee == aee.remove_all_listeners()
