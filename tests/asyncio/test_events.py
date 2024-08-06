import pytest
from utils import make_async_listener

from eventemitter import AsyncIOEventEmitter
from eventemitter.types import AsyncListenable


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_events(aee: AsyncIOEventEmitter) -> None:
    listener: AsyncListenable = make_async_listener()

    aee.on("foo", listener)
    assert aee.events() == ["foo"]

    aee.on("bar", listener)
    assert aee.events() == ["foo", "bar"]

    aee.remove_listener("bar", listener)
    assert aee.events() == ["foo"]
