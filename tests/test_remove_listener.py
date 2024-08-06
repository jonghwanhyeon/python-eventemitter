from typing import Any

from utils import fail, make_listener, trackable

from eventemitter import EventEmitter


# Test cases are based on https://github.com/browserify/events
def test_remove_listener1(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("hello", listener1)
    ee.on("remove_listener", fail)
    ee.remove_listener("hello", listener2)

    assert ee.listeners("hello") == [listener1]


def test_remove_listener2(ee: EventEmitter) -> None:
    @trackable
    def listener1(*args: Any, **kwargs: Any) -> None:
        ee.remove_listener("hello", listener2)

    listener2 = trackable(make_listener())

    ee.on("hello", listener1)
    ee.on("hello", listener2)

    ee.emit("hello")
    #  listener2 will still be called although it is removed by listener1
    assert listener1.hits == 1
    assert listener2.hits == 1

    ee.emit("hello")
    assert listener1.hits == 2
    assert listener2.hits == 1


def test_remove_listener3(ee: EventEmitter) -> None:
    assert ee == ee.remove_listener("foo", make_listener())


def test_remove_listener4(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("foo", listener1)
    ee.on("foo", listener2)
    assert ee.listeners("foo") == [listener1, listener2]

    ee.remove_listener("foo", listener1)
    assert ee.listeners("foo") == [listener2]

    ee.on("foo", listener1)
    assert ee.listeners("foo") == [listener2, listener1]

    ee.remove_listener("foo", listener1)
    assert ee.listeners("foo") == [listener2]
