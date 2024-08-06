import pytest
from utils import make_async_listener, trackable

from eventemitter import AsyncIOEventEmitter
from eventemitter.types import AsyncListenable
from eventemitter.utils import run_coroutine


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_inheritance() -> None:
    class MyEE(AsyncIOEventEmitter):
        def __init__(self, listener: AsyncListenable) -> None:
            super().__init__()

            self.once(1, listener)
            run_coroutine(self.emit, 1)
            self.remove_all_listeners()

    listener = trackable(make_async_listener())

    ee = MyEE(listener)  # noqa: F841
    assert listener.hits == 1
