from typing import Any

import pytest
from utils import trackable

from eventemitter import AsyncIOEventEmitter


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_prepend(aee: AsyncIOEventEmitter) -> None:
    count = 0

    @aee.on("foo")
    @trackable
    def on_foo1(*args: Any, **kwargs: Any) -> Any:
        assert count == 2

    @trackable
    def on_foo2(*args: Any, **kwargs: Any) -> Any:
        nonlocal count
        assert count == 1
        count += 1

    aee.prepend_once_listener("foo", on_foo2)

    @trackable
    def on_foo3(*args: Any, **kwargs: Any) -> Any:
        nonlocal count
        assert count == 0
        count += 1

    aee.prepend_once_listener("foo", on_foo3)

    await aee.emit_in_order("foo")
    assert on_foo1.hits == 1
    assert on_foo2.hits == 1
    assert on_foo3.hits == 1
