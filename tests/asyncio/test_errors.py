import pytest

from eventemitter import AsyncIOEventEmitter


# Test cases are based on https://github.com/browserify/events
@pytest.mark.asyncio
async def test_raise_and_catch_error(aee: AsyncIOEventEmitter) -> None:
    @aee.once("event")
    async def on_event(value: int) -> None:
        raise RuntimeError()

    with pytest.raises(RuntimeError):
        await aee.emit("event", 42)
