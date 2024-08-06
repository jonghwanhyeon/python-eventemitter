from utils import fail, make_listener, success

from eventemitter import EventEmitter


# Test cases are based on https://github.com/browserify/events
def test_listeners(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()
    listener3 = make_listener()
    listener4 = make_listener()

    ee.on("foo", listener1)
    ee.on("foo", listener2)
    ee.on("baz", listener3)
    ee.on(123, listener4)

    assert ee.listeners("foo") == [listener1, listener2]
    assert ee.listeners("bar") == []
    assert ee.listeners("baz") == [listener3]
    assert ee.listeners(123) == [listener4]


def test_side_effect_of_listeners(ee: EventEmitter) -> None:
    assert ee.listeners("foo") == []
    assert list(ee._events.keys()) == []

    ee.on("foo", fail)
    assert ee.listeners("foo") == [fail]

    ee.listeners("bar")

    ee.on("foo", success)
    assert ee.listeners("foo") == [fail, success]


def test_listeners1(ee: EventEmitter) -> None:
    listener = make_listener()

    ee.on("foo", listener)
    listeners = ee.listeners("foo")
    assert listeners == [listener]

    ee.remove_all_listeners("foo")
    assert ee.listeners("foo") == []

    assert listeners == [listener]


def test_listeners2(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("foo", listener1)
    listeners = ee.listeners("foo")
    assert listeners == [listener1]
    assert ee.listeners("foo") == [listener1]

    listeners.append(listener2)
    assert ee.listeners("foo") == [listener1]
    assert listeners == [listener1, listener2]


def test_listeners3(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("foo", listener1)
    listeners1 = ee.listeners("foo")

    ee.on("foo", listener2)
    listeners2 = ee.listeners("foo")

    assert listeners1 == [listener1]
    assert listeners2 == [listener1, listener2]


def test_listeners4(ee: EventEmitter) -> None:
    listener = make_listener()

    ee.once("foo", listener)
    assert ee.listeners("foo") == [listener]


def test_listeners5(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("foo", listener1)
    ee.once("foo", listener2)
    assert ee.listeners("foo") == [listener1, listener2]


def test_listeners6(ee: EventEmitter) -> None:
    class Foo(EventEmitter):
        pass

    foo = Foo()
    assert foo.listeners("foo") == []


def test_listeners7(ee: EventEmitter) -> None:
    listener = make_listener()

    ee.on("foo", listener)
    assert ee.listeners("foo") == [listener]

    ee.once("foo", listener)
    listeners = ee.listeners("foo")
    assert listeners == [listener, listener]
    assert ee.listeners("foo") == [listener, listener]

    ee.emit("foo")
    assert listeners == [listener, listener]
    assert ee.listeners("foo") == [listener]


def test_listeners8(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.once("foo", listener1)
    ee.on("foo", listener2)
    assert ee.listeners("foo") == [listener1, listener2]
