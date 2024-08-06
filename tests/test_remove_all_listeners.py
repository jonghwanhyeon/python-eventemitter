from __future__ import annotations

from utils import fail, make_listener, trackable

from eventemitter import EventEmitter
from eventemitter.types import Listenable


# Test cases are based on https://github.com/browserify/events
def test_remove_all_listeners1(ee: EventEmitter) -> None:
    listener = make_listener()

    ee.on("foo", listener)
    ee.on("bar", listener)
    ee.on("baz", listener)
    ee.on("baz", listener)

    foo_listeners = ee.listeners("foo")
    bar_listeners = ee.listeners("bar")
    baz_listeners = ee.listeners("baz")

    removed_events: list[str] = []

    @ee.on("remove_listener")
    def on_removed(event: str, listener: Listenable) -> None:
        removed_events.append(event)

    ee.remove_all_listeners("bar")
    ee.remove_all_listeners("baz")

    assert removed_events == ["bar", "baz", "baz"]
    assert ee.listeners("bar") == []
    assert ee.listeners("baz") == []

    # After calling remove_all_listeners(), the old listeners list should stay unchanged
    assert foo_listeners == [listener]
    assert bar_listeners == [listener]
    assert baz_listeners == [listener, listener]

    # After calling remove_all_listeners(), new listeners list is different from the old
    assert ee.listeners("bar") != bar_listeners
    assert ee.listeners("baz") != baz_listeners


def test_remove_all_listeners2(ee: EventEmitter) -> None:
    ee.on("foo", fail)
    ee.on("bar", fail)

    listener1 = trackable(make_listener())
    listener2 = trackable(make_listener())

    ee.on("remove_listener", listener1)
    ee.on("remove_listener", listener2)
    ee.remove_all_listeners()

    # Expect LIFO order
    assert [context.args[0] for context in listener1.contexts] == ["foo", "bar", "remove_listener"]
    assert [context.args[0] for context in listener2.contexts] == ["foo", "bar"]


def test_remove_all_listeners3(ee: EventEmitter) -> None:
    ee.on("remove_listener", fail)
    try:
        ee.remove_all_listeners("foo")
    except Exception:
        assert False


def test_remove_all_listeners4(ee: EventEmitter) -> None:
    expected = 2

    @ee.on("remove_listener")
    def on_remove_listener(event: str, listener: Listenable) -> None:
        nonlocal expected
        assert ee.listeners("baz") == [listener1, listener2][:expected]
        expected -= 1

    listener1 = make_listener(fail)
    listener2 = make_listener(fail)
    listener3 = make_listener(fail)

    ee.on("baz", listener1)
    ee.on("baz", listener2)
    ee.on("baz", listener3)
    assert ee.listeners("baz") == [listener1, listener2, listener3]

    ee.remove_all_listeners("baz")
    assert ee.listeners("baz") == []


def test_remove_all_listeners5(ee: EventEmitter) -> None:
    assert ee == ee.remove_all_listeners()
