from utils import fail, make_listener, trackable

from eventemitter import EventEmitter
from eventemitter.types import Listenable


# Test cases are based on https://github.com/browserify/events
def test_event_remove_listener1(ee: EventEmitter) -> None:
    listener = make_listener()

    ee.on("hello", listener)

    @ee.on("remove_listener")
    def on_remove_listener(event: str, listener: Listenable) -> None:
        assert event == "hello"
        assert listener == listener

    ee.remove_listener("hello", listener)

    assert ee.listeners("hello") == []


def test_event_remove_listener2(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("hello", listener1)
    ee.on("hello", listener2)

    @ee.once("remove_listener")
    def on_remove_listener1(event: str, listener: Listenable) -> None:
        assert event == "hello"
        assert listener == listener1
        assert ee.listeners("hello") == [listener2]

    ee.remove_listener("hello", listener1)
    assert ee.listeners("hello") == [listener2]

    @ee.once("remove_listener")
    @trackable
    def on_remove_listener2(event: str, listener: Listenable) -> None:
        assert event == "hello"
        assert listener == listener2
        assert ee.listeners("hello") == []

    ee.remove_listener("hello", listener2)
    assert ee.listeners("hello") == []
    assert on_remove_listener2.hits == 1


def test_event_remove_listener3(ee: EventEmitter) -> None:
    listener1 = make_listener(fail)
    listener2 = make_listener(fail)

    @ee.on("remove_listener")
    @trackable
    def on_remove_listener(event: str, listener: Listenable) -> None:
        if listener != listener1:
            return

        ee.remove_listener("foo", listener2)
        ee.emit("foo")

    ee.on("foo", listener1)
    ee.on("foo", listener2)
    ee.remove_listener("foo", listener1)

    assert on_remove_listener.hits == 2


def test_event_remove_listener4(ee: EventEmitter) -> None:
    listener1 = make_listener()
    listener2 = make_listener()

    ee.on("hello", listener1)
    ee.on("hello", listener2)

    @ee.once("remove_listener")
    @trackable
    def on_remove_listener1(event: str, listener: Listenable) -> None:
        assert event == "hello"
        assert listener == listener1
        assert ee.listeners("hello") == [listener2]

        @ee.once("remove_listener")
        @trackable
        def on_remove_listener2(event: str, listener: Listenable) -> None:
            assert event == "hello"
            assert listener == listener2
            assert ee.listeners("hello") == []

        ee.remove_listener("hello", listener2)
        assert ee.listeners("hello") == []
        assert on_remove_listener2.hits == 1

    ee.remove_listener("hello", listener1)
    assert ee.listeners("hello") == []
    assert on_remove_listener1.hits == 1


def test_event_remove_listener5(ee: EventEmitter) -> None:
    listener = make_listener()
    ee.once("hello", listener)

    @ee.on("remove_listener")
    @trackable
    def on_remove_listener(event: str, listener: Listenable) -> None:
        assert event == "hello"
        assert listener == listener

    ee.emit("hello")
    assert on_remove_listener.hits == 1
