import pytest
from utils import fail, make_async_listener, success

from eventemitter import AsyncIOEventEmitter


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_listeners(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()
    listener3 = make_async_listener()
    listener4 = make_async_listener()

    aee.on("foo", listener1)
    aee.on("foo", listener2)
    aee.on("baz", listener3)
    aee.on(123, listener4)

    assert aee.listeners("foo") == [listener1, listener2]
    assert aee.listeners("bar") == []
    assert aee.listeners("baz") == [listener3]
    assert aee.listeners(123) == [listener4]


@pytest.mark.asyncio
async def test_side_effect_of_listeners(aee: AsyncIOEventEmitter) -> None:
    assert aee.listeners("foo") == []
    assert list(aee._events.keys()) == []

    aee.on("foo", fail)
    assert aee.listeners("foo") == [fail]

    aee.listeners("bar")

    aee.on("foo", success)
    assert aee.listeners("foo") == [fail, success]


@pytest.mark.asyncio
async def test_listeners1(aee: AsyncIOEventEmitter) -> None:
    listener = make_async_listener()

    aee.on("foo", listener)
    listeners = aee.listeners("foo")
    assert listeners == [listener]

    aee.remove_all_listeners("foo")
    assert aee.listeners("foo") == []

    assert listeners == [listener]


@pytest.mark.asyncio
async def test_listeners2(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("foo", listener1)
    listeners = aee.listeners("foo")
    assert listeners == [listener1]
    assert aee.listeners("foo") == [listener1]

    listeners.append(listener2)
    assert aee.listeners("foo") == [listener1]
    assert listeners == [listener1, listener2]


@pytest.mark.asyncio
async def test_listeners3(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("foo", listener1)
    listeners1 = aee.listeners("foo")

    aee.on("foo", listener2)
    listeners2 = aee.listeners("foo")

    assert listeners1 == [listener1]
    assert listeners2 == [listener1, listener2]


@pytest.mark.asyncio
async def test_listeners4(aee: AsyncIOEventEmitter) -> None:
    listener = make_async_listener()

    aee.once("foo", listener)
    assert aee.listeners("foo") == [listener]


@pytest.mark.asyncio
async def test_listeners5(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("foo", listener1)
    aee.once("foo", listener2)
    assert aee.listeners("foo") == [listener1, listener2]


@pytest.mark.asyncio
async def test_listeners6(aee: AsyncIOEventEmitter) -> None:
    class Foo(AsyncIOEventEmitter):
        pass

    foo = Foo()
    assert foo.listeners("foo") == []


@pytest.mark.asyncio
async def test_listeners7(aee: AsyncIOEventEmitter) -> None:
    listener = make_async_listener()

    aee.on("foo", listener)
    assert aee.listeners("foo") == [listener]

    aee.once("foo", listener)
    listeners = aee.listeners("foo")
    assert listeners == [listener, listener]
    assert aee.listeners("foo") == [listener, listener]

    await aee.emit("foo")
    assert listeners == [listener, listener]
    assert aee.listeners("foo") == [listener]


@pytest.mark.asyncio
async def test_listeners8(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.once("foo", listener1)
    aee.on("foo", listener2)
    assert aee.listeners("foo") == [listener1, listener2]
