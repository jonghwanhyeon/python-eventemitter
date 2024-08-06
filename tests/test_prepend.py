from typing import Any

from utils import trackable

from eventemitter import EventEmitter


# Test cases are based on https://github.com/browserify/events
def test_prepend(ee: EventEmitter) -> None:
    count = 0

    @ee.on("foo")
    @trackable
    def on_foo1(*args: Any, **kwargs: Any) -> Any:
        assert count == 2

    @trackable
    def on_foo2(*args: Any, **kwargs: Any) -> Any:
        nonlocal count
        assert count == 1
        count += 1

    ee.prepend_once_listener("foo", on_foo2)

    @trackable
    def on_foo3(*args: Any, **kwargs: Any) -> Any:
        nonlocal count
        assert count == 0
        count += 1

    ee.prepend_once_listener("foo", on_foo3)

    ee.emit("foo")
    assert on_foo1.hits == 1
    assert on_foo2.hits == 1
    assert on_foo3.hits == 1
