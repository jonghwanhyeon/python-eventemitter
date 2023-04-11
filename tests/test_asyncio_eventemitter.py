import asyncio

import pytest

from eventemitter.asyncio import AsyncIOEventEmitter


def test_add_listener(aio_ee: AsyncIOEventEmitter, listeners):
    aio_ee.add_listener("alpha", listeners.aio_foo)
    assert set(aio_ee.event_names()) == {"alpha"}
    assert aio_ee.listeners("alpha") == [listeners.aio_foo]

    aio_ee.add_listener("alpha", listeners.aio_bar)
    assert set(aio_ee.event_names()) == {"alpha"}
    assert aio_ee.listeners("alpha") == [listeners.aio_foo, listeners.aio_bar]

    aio_ee.add_listener("alpha", listeners.baz)
    assert set(aio_ee.event_names()) == {"alpha"}
    assert aio_ee.listeners("alpha") == [listeners.aio_foo, listeners.aio_bar, listeners.baz]

    aio_ee.add_listener("beta", listeners.aio_foo)
    assert set(aio_ee.event_names()) == {"alpha", "beta"}


def test_remove_listener(aio_ee: AsyncIOEventEmitter, listeners):
    aio_ee.add_listener("alpha", listeners.aio_foo)
    aio_ee.add_listener("alpha", listeners.aio_bar)
    aio_ee.add_listener("alpha", listeners.aio_baz)
    aio_ee.add_listener("alpha", listeners.aio_bar)
    aio_ee.add_listener("alpha", listeners.aio_foo, once=True)

    aio_ee.remove_listener("alpha", listeners.aio_bar)
    assert aio_ee.listeners("alpha") == [listeners.aio_foo, listeners.aio_bar, listeners.aio_baz, listeners.aio_foo]

    aio_ee.remove_listener("alpha", listeners.aio_foo)
    assert aio_ee.listeners("alpha") == [listeners.aio_foo, listeners.aio_bar, listeners.aio_baz]


def test_on_alias(aio_ee: AsyncIOEventEmitter, listeners):
    aio_ee.on("alpha", listeners.aio_foo)
    assert set(aio_ee.event_names()) == {"alpha"}
    assert aio_ee.listeners("alpha") == [listeners.aio_foo]


def test_on_decorator(aio_ee: AsyncIOEventEmitter):
    @aio_ee.on("alpha")
    async def foo():
        pass

    assert set(aio_ee.event_names()) == {"alpha"}
    assert aio_ee.listeners("alpha") == [foo]


@pytest.mark.asyncio
async def test_emit(aio_ee: AsyncIOEventEmitter, listeners):
    container = []

    aio_ee.add_listener("alpha", listeners.aio_add_item)

    aio_ee.emit("alpha", container, 1)
    await asyncio.sleep(0.1)
    assert container == [1]

    aio_ee.emit("alpha", container, 2)
    await asyncio.sleep(0.1)
    assert container == [1, 2]

    aio_ee.add_listener("alpha", listeners.aio_add_item_twice)

    aio_ee.emit("alpha", container, 3)
    await asyncio.sleep(0.1)
    assert container == [1, 2, 3, 3, 3]


@pytest.mark.asyncio
async def test_once(aio_ee: AsyncIOEventEmitter, listeners):
    container = []

    aio_ee.once("alpha", listeners.aio_add_item)
    aio_ee.on("alpha", listeners.aio_add_item)
    aio_ee.once("alpha", listeners.aio_add_item_twice)
    aio_ee.on("alpha", listeners.aio_add_item_twice)

    aio_ee.emit("alpha", container, 1)
    await asyncio.sleep(0.1)
    assert container == [1, 1, 1, 1, 1, 1]

    aio_ee.emit("alpha", container, 2)
    await asyncio.sleep(0.1)
    assert container == [1, 1, 1, 1, 1, 1, 2, 2, 2]

    aio_ee.emit("alpha", container, 3)
    await asyncio.sleep(0.1)
    assert container == [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3]
