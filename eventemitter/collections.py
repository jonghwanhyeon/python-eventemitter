import collections
import sys
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

# fmt: off
if sys.version_info >= (3, 9):
    class UserList(collections.UserList[V], Generic[V]):
        __slots__ = ("data",)

    class UserDict(collections.UserDict[K, V], Generic[K, V]):
        __slots__ = ("data",)

else:
    class UserList(collections.UserList, Generic[V]):
        __slots__ = ("data",)

    class UserDict(collections.UserDict, Generic[K, V]):
        __slots__ = ("data",)
# fmt: on
