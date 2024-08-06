import pytest
from utils import fail, make_async_listener, trackable

from eventemitter import AsyncIOEventEmitter
from eventemitter.types import AsyncListenable


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_event_remove_listener1(aee: AsyncIOEventEmitter) -> None:
    listener = make_async_listener()

    aee.on("hello", listener)

    @aee.on("remove_listener")
    async def on_remove_listener(event: str, listener: AsyncListenable) -> None:
        assert event == "hello"
        assert listener == listener

    aee.remove_listener("hello", listener)

    assert aee.listeners("hello") == []


@pytest.mark.asyncio
async def test_event_remove_listener2(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("hello", listener1)
    aee.on("hello", listener2)

    @aee.once("remove_listener")
    async def on_remove_listener1(event: str, listener: AsyncListenable) -> None:
        assert event == "hello"
        assert listener == listener1
        assert aee.listeners("hello") == [listener2]

    aee.remove_listener("hello", listener1)
    assert aee.listeners("hello") == [listener2]

    @aee.once("remove_listener")
    @trackable
    async def on_remove_listener2(event: str, listener: AsyncListenable) -> None:
        assert event == "hello"
        assert listener == listener2
        assert aee.listeners("hello") == []

    aee.remove_listener("hello", listener2)
    assert aee.listeners("hello") == []
    assert on_remove_listener2.hits == 1


@pytest.mark.asyncio
async def test_event_remove_listener3(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener(fail)
    listener2 = make_async_listener(fail)

    @aee.on("remove_listener")
    @trackable
    async def on_remove_listener(event: str, listener: AsyncListenable) -> None:
        if listener != listener1:
            return

        aee.remove_listener("foo", listener2)
        await aee.emit("foo")

    aee.on("foo", listener1)
    aee.on("foo", listener2)
    aee.remove_listener("foo", listener1)

    assert on_remove_listener.hits == 2


@pytest.mark.asyncio
async def test_event_remove_listener4(aee: AsyncIOEventEmitter) -> None:
    listener1 = make_async_listener()
    listener2 = make_async_listener()

    aee.on("hello", listener1)
    aee.on("hello", listener2)

    @aee.once("remove_listener")
    @trackable
    async def on_remove_listener1(event: str, listener: AsyncListenable) -> None:
        assert event == "hello"
        assert listener == listener1
        assert aee.listeners("hello") == [listener2]

        @aee.once("remove_listener")
        @trackable
        async def on_remove_listener2(event: str, listener: AsyncListenable) -> None:
            assert event == "hello"
            assert listener == listener2
            assert aee.listeners("hello") == []

        aee.remove_listener("hello", listener2)
        assert aee.listeners("hello") == []
        assert on_remove_listener2.hits == 1

    aee.remove_listener("hello", listener1)
    assert aee.listeners("hello") == []
    assert on_remove_listener1.hits == 1


@pytest.mark.asyncio
async def test_event_remove_listener5(aee: AsyncIOEventEmitter) -> None:
    listener = make_async_listener()
    aee.once("hello", listener)

    @aee.on("remove_listener")
    @trackable
    def on_remove_listener(event: str, listener: AsyncListenable) -> None:
        assert event == "hello"
        assert listener == listener

    await aee.emit("hello")
    assert on_remove_listener.hits == 1
