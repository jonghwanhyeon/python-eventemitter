from __future__ import annotations

from typing import Any

from utils import make_listener, trackable

from eventemitter import EventEmitter


# Test cases are based on https://github.com/browserify/events
def test_emit(ee: EventEmitter) -> None:
    listener1 = trackable(make_listener())
    listener2 = trackable(make_listener())

    ee.on("foo", listener1)
    ee.on("bar", listener2)
    ee.on("bar", listener2)

    ee.emit("foo")
    assert listener1.contexts[-1].num_args == 0

    ee.emit("foo", None)
    assert listener1.contexts[-1].num_args == 1

    ee.emit("foo", None, None)
    assert listener1.contexts[-1].num_args == 2

    ee.emit("foo", None, None, None)
    assert listener1.contexts[-1].num_args == 3

    ee.emit("foo", None, None, None, None)
    assert listener1.contexts[-1].num_args == 4

    ee.emit("foo", None, None, None, None, None)
    assert listener1.contexts[-1].num_args == 5

    ee.emit("bar", None, None, None, None)
    assert listener2.contexts[-1].num_args == 4
    assert listener2.contexts[-2].num_args == 4


def test_side_effect_of_emit1(ee: EventEmitter) -> None:
    history: list[str] = []

    def listener1(*args: Any, **kwargs: Any) -> None:
        history.append("listener1")
        ee.on("foo", listener2)
        ee.on("foo", listener3)
        ee.remove_listener("foo", listener1)

    def listener2(*args: Any, **kwargs: Any) -> None:
        history.append("listener2")
        ee.remove_listener("foo", listener2)

    def listener3(*args: Any, **kwargs: Any) -> None:
        history.append("listener3")
        ee.remove_listener("foo", listener3)

    ee.on("foo", listener1)
    assert ee.listeners("foo") == [listener1]

    ee.emit("foo")
    assert ee.listeners("foo") == [listener2, listener3]
    assert history == ["listener1"]

    ee.emit("foo")
    assert ee.listeners("foo") == []
    assert history == ["listener1", "listener2", "listener3"]

    ee.emit("foo")
    assert ee.listeners("foo") == []
    assert history == ["listener1", "listener2", "listener3"]

    ee.on("foo", listener1)
    ee.on("foo", listener2)
    assert ee.listeners("foo") == [listener1, listener2]

    ee.remove_all_listeners("foo")
    assert ee.listeners("foo") == []


def test_side_effect_of_emit2(ee: EventEmitter) -> None:
    history: list[str] = []

    def listener1(*args: Any, **kwargs: Any) -> None:
        history.append("listener1")
        ee.remove_listener("foo", listener1)

    def listener2(*args: Any, **kwargs: Any) -> None:
        history.append("listener2")
        ee.remove_listener("foo", listener2)

    ee.on("foo", listener1)
    ee.on("foo", listener2)
    assert ee.listeners("foo") == [listener1, listener2]

    ee.emit("foo")
    assert history == ["listener1", "listener2"]
    assert ee.listeners("foo") == []
