from __future__ import annotations

from typing import Any, Callable, Hashable, List, Optional, TypeVar, Union

from typing_extensions import Protocol, Self, overload

from eventemitter.types import AsyncListenable, Listenable, Returns

L = TypeVar("L", bound=Union[Listenable, AsyncListenable])
F = TypeVar("F", bound=Union[Listenable, AsyncListenable])


# Reference: https://nodejs.org/api/events.html
class EventEmitterProtocol(Protocol[L]):
    """A protocol that describes the structural requirements for an `EventEmitter` class."""

    def add_listener(self, event: Hashable, listener: L) -> Self:
        """Add the `listener` function to the end of the listeners list for the event named `event`. Multiple calls passing the same combination of `event` and `listener` will result in the `listener` being added, and called, multiple times.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        ...

    def prepend_listener(self, event: Hashable, listener: L) -> Self:
        """Add the `listener` function to the *beginning* of the listeners list for the event named `event`. Multiple calls passing the same combination of `event` and `listener` will result in the `listener` being added, and called, multiple times.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        ...

    def prepend_once_listener(self, event: Hashable, listener: L) -> Self:
        """Add a **one-time** `listener` function for the event named `event` to the *beginning* of the listeners list. The next time `event` is triggered, this `listener` is removed, and then invoked.

        Args:
            event: The name of the event
            listener: The callback function

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        ...

    def emit(self, event: Hashable, *args: Any, **kwargs: Any) -> Returns[bool]:
        """Call each of the listeners registered for the event named `event`, passing the supplied arguments to each.

        Args:
            event: The name of the event
            *args: Arbitrary positional arguments
            **kwargs: Arbitrary keyword arguments

        Returns:
            (bool): `True` if the `event` had listeners, `False` otherwise.
        """
        ...

    def events(self) -> List[Hashable]:
        """Return a list of the events for which the emitter has registered listeners.

        Returns:
            A list of the `event`s
        """
        ...

    def listeners(self, event: Hashable) -> List[L]:
        """Return a copy of the list of listeners for the event named `event`.

        Args:
            event: The name of the event

        Returns:
           A copy of the list of listeners for the event named `event`.
        """
        ...

    def off(self, event: Hashable, listener: L) -> Self:
        """Alias for `remove_listener()`.

        Args:
            event: The name of the event
            listener: The listener to remove

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        ...

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
            (Callable[[F], F]): A decorator that adds the decorated function to the listeners list for the event named `event`.
        """
        ...

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
            (Callable[[F], F]): A decorator that adds the decorated function as a **one-time** `listener` for the event named `event`.
        """
        ...

    def remove_all_listeners(self, event: Optional[Hashable] = None) -> Self:
        """Remove all listeners, or those of the specified `event`.

        Args:
            event: The name of the event

        Returns:
            An instance of the `EventEmitter`, so that calls can be chained.
        """
        ...

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
        ...
