from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Hashable, List, Optional, Type, TypeVar, Union

from typing_extensions import Self, overload

from eventemitter.events import Events
from eventemitter.handlers import AbstractHandler, AsyncHandler, Handler
from eventemitter.protocol import EventEmitterProtocol
from eventemitter.types import AsyncListenable, Listenable, Returns
from eventemitter.utils import run_coroutine

L = TypeVar("L", bound=Union[Listenable, AsyncListenable])  # for classes
H = TypeVar("H", bound=AbstractHandler)

F = TypeVar("F", bound=Union[Listenable, AsyncListenable])  # for functions


# Reference: https://nodejs.org/api/events.html
class AbstractEventEmitter(ABC, EventEmitterProtocol[L], Generic[L, H]):
    """An abstract class for `EventEmitter` classes.

    This class provides a generic implementation for `EventEmitter`s that can manage and emit listeners for events.
    All `EventEmitter`s emit the event `"new_listener"` when new listeners are added and `"remove_listener"` when existing listeners are removed.
    """

    __slots__ = ("_events",)

    _handler_cls: Type[H]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an instance of [`AbstractEventEmitter`][eventemitter.AbstractEventEmitter].

        Args:
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments
        """
        # To support cooperative multiple inheritance
        # Reference: https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        super().__init__(*args, **kwargs)
        self._events: Events[L, H] = Events[L, H]()

    def add_listener(self, event: Hashable, listener: L) -> Self:
        """Add the `listener` function to the end of the listeners list for the event named `event`. Multiple calls passing the same combination of `event` and `listener` will result in the `listener` being added, and called, multiple times.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        return self._append_handler(event, self._handler_cls.from_func(listener, once=False))

    def prepend_listener(self, event: Hashable, listener: L) -> Self:
        """Add the `listener` function to the *beginning* of the listeners list for the event named `event`. Multiple calls passing the same combination of `event` and `listener` will result in the `listener` being added, and called, multiple times.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        return self._prepend_handler(event, self._handler_cls.from_func(listener, once=False))

    def prepend_once_listener(self, event: Hashable, listener: L) -> Self:
        """Add a **one-time** `listener` function for the event named `event` to the *beginning* of the listeners list. The next time `event` is triggered, this `listener` is removed, and then invoked.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        return self._prepend_handler(event, self._handler_cls.from_func(listener, once=True))

    @abstractmethod
    def emit(self, event: Hashable, *args: Any, **kwargs: Any) -> Returns[bool]:
        """Call each of the listeners registered for the event named `event`, passing the supplied arguments to each.

        Args:
            event: The name of the event
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments

        Returns:
            (bool): `True` if the `event` had listeners, `False` otherwise.
        """
        raise NotImplementedError()

    def events(self) -> List[Hashable]:
        """Return a list of the events for which the emitter has registered listeners.

        Returns:
            A list of the `event`s
        """
        return list(self._events.keys())

    def listeners(self, event: Hashable) -> List[L]:
        """Return a copy of the list of listeners for the event named `event`.

        Args:
            event: The name of the event

        Returns:
            A copy of the list of listeners for the event named `event`.
        """
        return self._events.listeners(event)

    def off(self, event: Hashable, listener: L) -> Self:
        """Alias for `remove_listener()`.

        Args:
            event: The name of the event
            listener: The listener to remove

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        return self.remove_listener(event, listener)

    @overload
    def on(self, event: Hashable, listener: L) -> Self: ...
    @overload
    def on(self, event: Hashable) -> Callable[[F], F]: ...

    def on(self, event: Hashable, listener: Optional[F] = None) -> Union[Self, Callable[[F], F]]:
        """Add the `listener` function to the end of the listeners list for the event named `event` if a `listener` is provided, or return a decorator to add the decorated function as a `listener` if no `listener` is provided.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            (Self): An instance of the `EventEmitter`, so that calls can be chained if a `listener` is provided.
            (Callable[[F], F]): A decorator that adds the decorated function to the listeners list for the event named `event` if no `listener` is provided.
        """

        def decorator(listener: F) -> F:
            self._append_handler(event, self._handler_cls.from_func(listener, once=False))
            return listener

        if listener is not None:
            decorator(listener)

        return decorator if listener is None else self

    @overload
    def once(self, event: Hashable, listener: L) -> Self: ...
    @overload
    def once(self, event: Hashable) -> Callable[[F], F]: ...

    def once(self, event: Hashable, listener: Optional[F] = None) -> Union[Self, Callable[[F], F]]:
        """Add a **one-time** `listener` function to the end of the listeners list for the event named `event` if a `listener` is provided, or return a decorator that adds the decorated function as a **one-time** `listener` if no `listener` is provided.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            (Self): An instance of the `EventEmitter`, so that calls can be chained if a `listener` is provided.
            (Callable[[F], F]): A decorator that adds the decorated function as a **one-time** `listener` for the event named `event` if no `listener` is provided.
        """

        def decorator(listener: F) -> F:
            self._append_handler(event, self._handler_cls.from_func(listener, once=True))
            return listener

        if listener is not None:
            decorator(listener)

        return decorator if listener is None else self

    def remove_all_listeners(self, event: Optional[Hashable] = None) -> Self:
        """Remove all listeners, or those of the specified `event`.

        Args:
            event: The name of the event

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        if event is None:
            for event in self.events():
                self.remove_all_listeners(event)
        else:
            for handler in reversed(self._events.handlers(event)):
                self._remove_handler(event, handler)

        return self

    def remove_listener(self, event: Hashable, listener: L) -> Self:
        """Remove the specified `listener` from the listener list for the event named `event`.

           `remove_listener()` will remove, at most, one instance of a listener from the listener list.
           If any single listener has been added multiple times to the listener list for the specified `event`, then `remove_listener()` must be called multiple times to remove each instance.

           Once an event is emitted, all listeners attached to it at the time of emitting are called in order.
           This implies that any `remove_listener()` or `remove_all_listeners()` calls after emitting and before the last listener finishes execution will not remove them from emit() in progress.
           Subsequent events behave as expected.

           When a single function has been added as a handler multiple times for a single event, `remove_listener()` will remove the most recently added instance.

        Args:
            event: The name of the event
            listener: The listener to remove

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        return self._remove_handler(event, listener)

    def _append_handler(self, event: Hashable, handler: H) -> Self:
        self._emit_until_complete("new_listener", event, handler.func)
        self._events[event].append(handler)
        return self

    def _prepend_handler(self, event: Hashable, handler: H) -> Self:
        self._emit_until_complete("new_listener", event, handler.func)
        self._events[event].prepend(handler)
        return self

    @overload
    def _remove_handler(self, event: Hashable, target: H) -> Self: ...
    @overload
    def _remove_handler(self, event: Hashable, target: Union[Listenable, AsyncListenable]) -> Self: ...

    def _remove_handler(self, event: Hashable, target: Union[H, Listenable, AsyncListenable]) -> Self:
        if event not in self._events:
            return self

        try:
            if isinstance(target, self._handler_cls):
                handler = self._events[event].remove(target, last=True)
            else:
                handler = self._events[event].remove_by_id(target, last=True)

            self._emit_until_complete("remove_listener", event, handler.func)
        except ValueError:
            pass

        if not self._events[event]:
            del self._events[event]

        return self

    @abstractmethod
    def _emit_until_complete(self, event: Hashable, *args: Any, **kwargs: Any) -> None: ...


class EventEmitter(AbstractEventEmitter[Listenable, Handler]):
    """An `EventEmitter` class that executes listeners synchronously.

    This class allows you to add and remove listeners for specified events and emit those events with arbitrary arguments.
    When a new listener is added, the `EventEmitter` emits a `"new_listener"` event. When an existing listener is removed, the `EventEmitter` emits a `"remove_listener"` event.

    # Events

    **Event: `"new_listener"`**

    The `EventEmitter` instance will emit its own `"new_listener"` event before a `listener` is added to its internal list of listeners.
    Listeners registered for the `"new_listener"` event are passed the `event` name and a reference to the `listener` being added.

    Name       | Type                                  | Descriptions
    ---------- | ------------------------------------- | ----------------------------------------
    `event`    | [Hashable][typing.Hashable]           | The name of the event being listened for
    `listener` | [Listenable][eventemitter.Listenable] | The event handler function


    **Event: `"remove_listener"`**

    The `"remove_listener"` event is emitted after the `listener` is removed.

    Name       | Type                                  | Descriptions
    ---------- | ------------------------------------- | ----------------------------------------
    `event`    | [Hashable][typing.Hashable]           | The name of the event being listened for
    `listener` | [Listenable][eventemitter.Listenable] | The event handler function
    """

    _handler_cls = Handler
    _executor = staticmethod(lambda func, *args, **kwargs: func(*args, **kwargs))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an instance of `EventEmitter`.

        Args:
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)

    def emit(self, event: Hashable, *args: Any, **kwargs: Any) -> bool:
        """Call each of the listeners registered for the event named `event`, in the order they were registered, passing the supplied arguments to each.

        Args:
            event: The name of the event
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments

        Returns:
            (bool): `True` if the `event` had listeners, `False` otherwise.
        """
        if event not in self._events:
            return False

        for handler in self._events.handlers(event):
            if handler.once:
                self._remove_handler(event, handler)

            handler(*args, **kwargs)

        return True

    def _emit_until_complete(self, event: Hashable, *args: Any, **kwargs: Any) -> None:
        self.emit(event, *args, **kwargs)


class AsyncIOEventEmitter(AbstractEventEmitter[Union[Listenable, AsyncListenable], AsyncHandler]):
    r"""An `AsyncIOEventEmitter` class that executes listeners asynchronously.

    This class allows you to add and remove listeners for specified events and emit those events with arbitrary arguments in a non-blocking manner.
    When a new listener is added, the `AsyncIOEventEmitter` emits a `"new_listener"` event. When an existing listener is removed, it emits a `"remove_listener"` event.

    # Events

    **Event: `"new_listener"`**

    The `AsyncIOEventEmitter` instance will emit its own `"new_listener"` event before a `listener` is added to its internal list of listeners.
    Listeners registered for the `"new_listener"` event are passed the `event` name and a reference to the `listener` being added.

    Notes:
        - A new listener is **guaranteed** to be added to the internal list of listeners **only after** all listeners registered for the `"new_listener"` event have been scheduled and **have completed their execution**.
        - As a side effect of this implementation, `add_listener()`, `prepend_listener()`, `prepend_once_listener()`, `on()`, and `once()` methods operate in a blocking manner.

    Name       | Type                                                                                         | Descriptions
    ---------- | -------------------------------------------------------------------------------------------- | ----------------------------------------
    `event`    | [`Hashable`][typing.Hashable]                                                                | The name of the event being listened for
    `listener` | [`Listenable`][eventemitter.Listenable] \| [`AsyncListenable`][eventemitter.AsyncListenable] | The event handler function


    **Event: `"remove_listener"`**

    The `"remove_listener"` event is emitted after the `listener` is removed.

    Name       | Type                                                                                         | Descriptions
    ---------- | -------------------------------------------------------------------------------------------- | ----------------------------------------
    `event`    | [`Hashable`][typing.Hashable]                                                                | The name of the event being listened for
    `listener` | [`Listenable`][eventemitter.Listenable] \| [`AsyncListenable`][eventemitter.AsyncListenable] | The event handler function

    Notes:
        - Similarly to `"new_listener"` event, `remove_listener()`, `remove_all_listeners()`, and `off()` methods return **only after** waiting for all `"remove_listener"` event listeners to complete.
    """

    _handler_cls = AsyncHandler

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize an instance of `AsyncIOEventEmitter`.

        Args:
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)

    async def emit(self, event: Hashable, *args: Any, **kwargs: Any) -> bool:
        """Call each of the listeners registered for the event named `event`, simultaneously, passing the supplied arguments to each.

        Args:
            event: The name of the event
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments

        Returns:
            (bool): `True` if the `event` had listeners, `False` otherwise.
        """
        if event not in self._events:
            return False

        tasks = set()
        for handler in self._events.handlers(event):
            if handler.once:
                self._remove_handler(event, handler)

            tasks.add(handler(*args, **kwargs))

        await asyncio.gather(*tasks)

        return True

    async def emit_in_order(self, event: Hashable, *args: Any, **kwargs: Any) -> bool:
        """Call each of the listeners registered for the event named `event`, in the order they were registered, passing the supplied arguments to each.

        Args:
            event: The name of the event
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments

        Returns:
            (bool): `True` if the `event` had listeners, `False` otherwise.
        """
        if event not in self._events:
            return False

        for handler in self._events.handlers(event):
            if handler.once:
                self._remove_handler(event, handler)

            await handler(*args, **kwargs)

        return True

    def _emit_until_complete(self, event: Hashable, *args: Any, **kwargs: Any) -> None:
        run_coroutine(self.emit, event, *args, **kwargs)
