from __future__ import annotations

from typing import Any

from utils import fail, make_listener, trackable

from eventemitter import EventEmitter


# Test cases are based on https://github.com/browserify/events
def test_once1(ee: EventEmitter) -> None:
    @ee.once("foo")
    def on_foo(value: int) -> None:
        assert value == 42
        assert ee.listeners("foo") == []

    ee.emit("foo", 42)


def test_once2(ee: EventEmitter) -> None:
    @ee.once("foo")
    def on_foo(*values: int) -> None:
        assert values == (42, 24)

    ee.emit("foo", 42, 24)


def test_once3(ee: EventEmitter) -> None:
    listener1 = trackable(make_listener())
    ee.once("hello", listener1)

    ee.emit("hello", "a", "b")
    ee.emit("hello", "a", "b")
    ee.emit("hello", "a", "b")
    ee.emit("hello", "a", "b")
    assert listener1.hits == 1

    ee.once("foo", fail)
    ee.remove_listener("foo", fail)
    ee.emit("foo")

    @ee.once("bar")
    @trackable
    def listener2(*args: Any, **kwargs: Any) -> None:
        ee.emit("bar")

    @ee.once("bar")
    @trackable
    def listener3(*args: Any, **kwargs: Any) -> None:
        pass

    ee.emit("bar")
    assert listener2.hits == 1
    assert listener3.hits == 2


def test_once4() -> None:
    for i in range(5):
        ee = EventEmitter()
        parameters: list[str] = ["foo"]

        for j in range(0, i):
            parameters.append(str(j))

        @ee.once("foo")
        @trackable
        def on_foo(*arguments: str) -> None:
            assert parameters[1:] == list(arguments)

        ee.emit(*parameters)
        assert on_foo.hits == 1
