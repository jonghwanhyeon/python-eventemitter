from typing import Any

import pytest
from utils import fail, make_async_listener, trackable

from eventemitter import AsyncIOEventEmitter


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_remove_listener1(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("hello", listener1)
    aee.on("remove_listener", fail)
    aee.remove_listener("hello", listener2)

    assert aee.listeners("hello") == [listener1]


@pytest.mark.asyncio
async def test_remove_listener2(aee: AsyncIOEventEmitter) -> None:
    @trackable
    def listener1(*args: Any, **kwargs: Any) -> None:
        aee.remove_listener("hello", listener2)

    listener2 = trackable(make_async_listener())

    aee.on("hello", listener1)
    aee.on("hello", listener2)

    await aee.emit("hello")
    #  listener2 will still be called although it is removed by listener1
    assert listener1.hits == 1
    assert listener2.hits == 1

    await aee.emit("hello")
    assert listener1.hits == 2
    assert listener2.hits == 1


@pytest.mark.asyncio
async def test_remove_listener3(aee: AsyncIOEventEmitter) -> None:
    assert aee == aee.remove_listener("foo", make_async_listener())


@pytest.mark.asyncio
async def test_remove_listener4(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("foo", listener1)
    aee.on("foo", listener2)
    assert aee.listeners("foo") == [listener1, listener2]

    aee.remove_listener("foo", listener1)
    assert aee.listeners("foo") == [listener2]

    aee.on("foo", listener1)
    assert aee.listeners("foo") == [listener2, listener1]

    aee.remove_listener("foo", listener1)
    assert aee.listeners("foo") == [listener2]
