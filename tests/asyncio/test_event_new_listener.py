from __future__ import annotations

import pytest
from utils import fail, make_async_listener, trackable

from eventemitter import AsyncIOEventEmitter
from eventemitter.types import AsyncListenable


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_event_new_listener1(aee: AsyncIOEventEmitter) -> None:
    events: set[str] = set()
    listeners: set[AsyncListenable] = set()

    @aee.on("new_listener")
    async def on_new_listener1(event: str, listener: AsyncListenable) -> None:
        if event == "new_listener":
            return

        events.add(event)
        listeners.add(listener)

    @trackable
    async def hello(a: str, b: str) -> None:
        assert a == "a"
        assert b == "b"

    @aee.once("new_listener")
    async def on_new_listener2(event: str, listener: AsyncListenable) -> None:
        assert event == "hello"
        assert listener == hello

        listeners = aee.listeners("hello")
        assert listeners == []

    aee.on("hello", hello)
    aee.once("foo", fail)

    assert events == {"hello", "foo"}
    assert listeners == {hello, fail}

    await aee.emit("hello", "a", "b")
    assert hello.hits == 1


@pytest.mark.asyncio
async def test_event_new_listener2(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener(fail)
    listener2 = make_async_listener(fail)

    @aee.once("new_listener")
    async def on_new_listener1(event: str, listener: AsyncListenable) -> None:
        listeners = aee.listeners("hello")
        assert listeners == []

        @aee.once("new_listener")
        async def on_new_listener2(event: str, listener: AsyncListenable) -> None:
            listeners = aee.listeners("hello")
            assert listeners == []

        aee.on("hello", listener2)

    aee.on("hello", listener1)

    assert aee.listeners("hello") == [listener2, listener1]
