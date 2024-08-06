from utils import make_listener

from eventemitter import EventEmitter
from eventemitter.types import Listenable


# Test cases are based on https://github.com/browserify/events
def test_events(ee: EventEmitter) -> None:
    listener: Listenable = make_listener()

    ee.on("foo", listener)
    assert ee.events() == ["foo"]

    ee.on("bar", listener)
    assert ee.events() == ["foo", "bar"]

    ee.remove_listener("bar", listener)
    assert ee.events() == ["foo"]
