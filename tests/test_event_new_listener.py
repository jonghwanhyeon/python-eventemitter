from __future__ import annotations

from utils import fail, make_listener, trackable

from eventemitter import EventEmitter
from eventemitter.types import Listenable


# Test cases are based on https://github.com/browserify/events
def test_event_new_listener1(ee: EventEmitter) -> None:
    events: list[str] = []
    listeners: list[Listenable] = []

    @ee.on("new_listener")
    def on_new_listener1(event: str, listener: Listenable) -> None:
        if event == "new_listener":
            return

        events.append(event)
        listeners.append(listener)

    @trackable
    def hello(a: str, b: str) -> None:
        assert a == "a"
        assert b == "b"

    @ee.once("new_listener")
    def on_new_listener2(event: str, listener: Listenable) -> None:
        assert event == "hello"
        assert listener == hello

        listeners = ee.listeners("hello")
        assert listeners == []

    ee.on("hello", hello)
    ee.once("foo", fail)

    assert events == ["hello", "foo"]
    assert listeners == [hello, fail]

    ee.emit("hello", "a", "b")
    assert hello.hits == 1


def test_event_new_listener2(ee: EventEmitter) -> None:
    listener1 = make_listener(fail)
    listener2 = make_listener(fail)

    @ee.once("new_listener")
    def on_new_listener1(event: str, listener: Listenable) -> None:
        listeners = ee.listeners("hello")
        assert listeners == []

        @ee.once("new_listener")
        def on_new_listener2(event: str, listener: Listenable) -> None:
            listeners = ee.listeners("hello")
            assert listeners == []

        ee.on("hello", listener2)

    ee.on("hello", listener1)

    assert ee.listeners("hello") == [listener2, listener1]
