from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union, overload

from typing_extensions import Self

from eventemitter.core.events import Events, Handler
from eventemitter.core.executor import Executor

R = TypeVar("R")
C = Callable[..., R]

# Reference: https://nodejs.org/api/events.html
class EventEmitter(Generic[R]):
    _executor_cls: Type[Executor[R]]

    def __init__(self, *args: Any, **kwargs: Any):
        # Support for cooperative multiple inheritance
        # Reference: https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        super().__init__(*args, **kwargs)

        self._executor = self._executor_cls()
        self._events = Events[R]()

    def add_listener(self, event: str, listener: C[R], once: bool = False) -> Self:
        """Adds the `listener` function to the end of the listeners list for the event named `event`.

        Parameters:
            event: The name of the event
            listener: The callback function
            once: The `listener` is called at most once if `True`. Defaults to False.

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained.
        """
        self._events.add_handler(
            event,
            Handler(id=id(listener), func=listener, once=once),
        )
        return self

    def emit(self, event: str, *args: Any, **kwargs: Any):
        """Calls each of the listeners registered for the event named `event`, \
           in the order they were registered, passing the supplied arguments to each.

        Parameters:
            event: The name of the event

        Returns:
            `True` if the event had listeners, `False` otherwise.
        """
        for handler in self._events.handlers(event):
            self._executor.execute(handler, *args, **kwargs)

            if handler.once:
                self._events.remove_handler(event, handler)

    def event_names(self) -> list[str]:
        """Returns a list of the events for which the emitter has registered listeners.

        Returns:
            A list of the events
        """
        return self._events.names()

    def listeners(self, event: str) -> list[C[R]]:
        """Returns a copy of the list of listeners for the event named `event`.

        Parameters:
            event: The name of the event

        Returns:
            A list of listeners for the event named `event`.
        """
        return [handler.func for handler in self._events.handlers(event)]

    def off(self, event: str, listener: C[R]) -> Self:
        """Alias for `EventEmitter.remove_listener()`."""
        return self.remove_listener(event, listener)

    @overload
    def on(self, event: str) -> Callable[[C[R]], C[R]]:
        """Decorator for `EventEmitter.add_listener()`.
           The decorated function is used as `listener`.

        Parameters:
            event: The name of the event

        Returns:
            A decorator for adding the decorated function to the end of the listeners list for the event named `event`.
        """
        ...

    @overload
    def on(self, event: str, listener: C[R]) -> Self:
        """Alias for `EventEmitter.add_listener()`.

        Parameters:
            event: The name of the event
            listener: The callback function. Defaults to None.

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained.
        """
        ...

    def on(
        self,
        event: str,
        listener: Optional[C[R]] = None,
    ) -> Union[Self, Callable[[C[R]], C[R]]]:
        """Alias for `EventEmitter.add_listener()`. \
           If `listener` is not provided, the decorated function is used as `listener`.

        Parameters:
            event: The name of the event
            listener: The callback function. Defaults to None.

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained if `listener` is provided.
            Otherwise, a decorator for adding the decorated function to the end of the listeners list for the event named `event`.
        """
        if listener is not None:
            return self.add_listener(event, listener)

        def decorator(listener: C[R]) -> C[R]:
            self.add_listener(event, listener)
            return listener

        return decorator

    @overload
    def once(self, event: str) -> Callable[[C[R]], C[R]]:
        """Decorator for `EventEmitter.add_listener(once=True)`. \
           The decorated function is used as `listener`.

        Parameters:
            event: The name of the event

        Returns:
            A decorator for adding the decorated function to the end of the listeners list for the event named `event`.
        """
        ...

    @overload
    def once(self, event: str, listener: C[R]) -> Self:
        """Alias for `EventEmitter.add_listener(once=True)`.

        Parameters:
            event: The name of the event
            listener: The callback function. Defaults to None.

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained if `listener` is provided.
            Otherwise, a decorator for adding the decorated function to the end of the listeners list for the event named `event`.
        """
        ...

    def once(
        self,
        event: str,
        listener: Optional[C[R]] = None,
    ) -> Union[Self, Callable[[C[R]], C[R]]]:
        """Alias for `EventEmitter.add_listener(once=True)`. \
           If `listener` is not provided, the decorated function is used as `listener`.

        Parameters:
            event: The name of the event
            listener: The callback function. Defaults to None.

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained if `listener` is provided.
            Otherwise, a decorator for adding the decorated function to the end of the listeners list for the event named `event`.
        """
        if listener is not None:
            return self.add_listener(event, listener, once=True)

        def decorator(listener: C[R]) -> C[R]:
            self.add_listener(event, listener, once=True)
            return listener

        return decorator

    def remove_all_listeners(self, event: Optional[str] = None) -> Self:
        """Removes all listeners, or those of the specified `event`.

        Parameters:
            event: The name of the event

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained.
        """
        if event is None:
            self._events.clear()
        elif event in self._events:
            del self._events[event]

        return self

    def remove_listener(self, event: str, listener: C[R]) -> Self:
        """Removes the specified `listener` from the listener list for the event named `event`.

        Parameters:
            event: The name of the event
            listener: The listener to remove

        Returns:
            A reference to the `EventEmitter`, so that calls can be chained.
        """
        self._events.remove_handler_by_id(event, id(listener))
        return self
