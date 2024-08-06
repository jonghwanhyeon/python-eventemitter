from utils import make_listener, trackable

from eventemitter import EventEmitter
from eventemitter.types import Listenable


# Test cases are based on https://github.com/browserify/events
def test_inheritance() -> None:
    class MyEE(EventEmitter):
        def __init__(self, listener: Listenable) -> None:
            super().__init__()

            self.once(1, listener)
            self.emit(1)
            self.remove_all_listeners()

    listener = trackable(make_listener())

    ee = MyEE(listener)  # noqa: F841
    assert listener.hits == 1
