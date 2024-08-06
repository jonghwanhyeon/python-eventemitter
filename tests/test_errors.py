import pytest

from eventemitter import EventEmitter


# Test cases are based on https://github.com/browserify/events
def test_raise_and_catch_error(ee: EventEmitter) -> None:
    @ee.once("event")
    def on_event(value: int) -> None:
        raise RuntimeError()

    with pytest.raises(RuntimeError):
        ee.emit("event", 42)
