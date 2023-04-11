from eventemitter import EventEmitter


def test_add_listener(ee: EventEmitter, listeners):
    ee.add_listener("alpha", listeners.foo)
    assert set(ee.event_names()) == {"alpha"}
    assert ee.listeners("alpha") == [listeners.foo]

    ee.add_listener("alpha", listeners.bar)
    assert set(ee.event_names()) == {"alpha"}
    assert ee.listeners("alpha") == [listeners.foo, listeners.bar]

    ee.add_listener("alpha", listeners.baz)
    assert set(ee.event_names()) == {"alpha"}
    assert ee.listeners("alpha") == [listeners.foo, listeners.bar, listeners.baz]

    ee.add_listener("beta", listeners.foo)
    assert set(ee.event_names()) == {"alpha", "beta"}


def test_remove_listener(ee: EventEmitter, listeners):
    ee.add_listener("alpha", listeners.foo)
    ee.add_listener("alpha", listeners.bar)
    ee.add_listener("alpha", listeners.baz)
    ee.add_listener("alpha", listeners.bar)
    ee.add_listener("alpha", listeners.foo, once=True)

    ee.remove_listener("alpha", listeners.bar)
    assert ee.listeners("alpha") == [listeners.foo, listeners.bar, listeners.baz, listeners.foo]

    ee.remove_listener("alpha", listeners.foo)
    assert ee.listeners("alpha") == [listeners.foo, listeners.bar, listeners.baz]


def test_on_alias(ee: EventEmitter, listeners):
    ee.on("alpha", listeners.foo)
    assert set(ee.event_names()) == {"alpha"}
    assert ee.listeners("alpha") == [listeners.foo]


def test_on_decorator(ee: EventEmitter):
    @ee.on("alpha")
    def foo():
        pass

    assert set(ee.event_names()) == {"alpha"}
    assert ee.listeners("alpha") == [foo]


def test_emit(ee: EventEmitter, listeners):
    container = []

    ee.add_listener("alpha", listeners.add_item)

    ee.emit("alpha", container, 1)
    assert container == [1]

    ee.emit("alpha", container, 2)
    assert container == [1, 2]

    ee.add_listener("alpha", listeners.add_item_twice)

    ee.emit("alpha", container, 3)
    assert container == [1, 2, 3, 3, 3]


def test_once(ee: EventEmitter, listeners):
    container = []

    ee.once("alpha", listeners.add_item)
    ee.on("alpha", listeners.add_item)
    ee.once("alpha", listeners.add_item_twice)
    ee.on("alpha", listeners.add_item_twice)

    ee.emit("alpha", container, 1)
    assert container == [1, 1, 1, 1, 1, 1]

    ee.emit("alpha", container, 2)
    assert container == [1, 1, 1, 1, 1, 1, 2, 2, 2]

    ee.emit("alpha", container, 3)
    assert container == [1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3]
