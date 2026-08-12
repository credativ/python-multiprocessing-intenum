"""A multiprocessing safe shared object for `IntEnum` enum values."""

import multiprocessing
from enum import IntEnum
from multiprocessing.synchronize import Lock, RLock
from types import get_original_bases
from typing import Any, get_args, get_origin

from ._version import version as __version__  # noqa: F401


class IntEnumValue[T: IntEnum]:
    """A multiprocessing safe shared object for `IntEnum` enum values."""

    # Pre-initialize type here to avoid numerous type ignores elsewhere
    EnumType: type[T | IntEnum] = IntEnum

    @classmethod
    def __init_subclass__(cls) -> None:  # noqa: D105
        # To provide extended type checking, we need to determine the specigic
        # type of IntEnum we have been subclassed with and set the EnumType
        # attribute accordingly.
        #
        # The classes that we have been subclassed from can fall into the
        # following cases:
        # 1. a generic class with a specific type given
        # 2. a subclass of a generic class without a new specific type given
        # 3. our base class or a subclass of it without a specific type given
        # 4. a class that is not a subclass of us, e.g. a mixin class
        #
        # In case 1, our original bases do contain the generic class with its
        # type argument included.
        # In cases 2 and 3, our original bases do contain the class itself only.
        # ie. with the type argument *not* included.
        # In case 2, the class or a parent of it must itself have been case 1,
        # thus our EnumType attribute is resolved to the correct value as per
        # MRO already.
        # In case 3, the EnumType attribute remains the default and no extended
        # type checking will happen.
        # In case 4, the class is to be ignored.
        #
        # Multiple inheritance (as in case 4) needs to be taken into account,
        # we thus iterate over original bases in MRO and terminate if one of
        # the conclusive cases 1-3 is identified.
        #
        for base in get_original_bases(cls):
            # check if parent is a generic class that is a subclass of us (case 1)
            origin = get_origin(base)
            if origin is not None and issubclass(origin, IntEnumValue):
                # set EnumType to the specific type of the generic class
                cls.EnumType = get_args(base)[0]
                break

            # check if parent is a subclass of us (cases 2 and 3)
            if isinstance(base, type) and issubclass(base, IntEnumValue):
                break

    def __init__(self, value: T | str, lock: None | Lock | RLock = None) -> None:
        """Initialize IntEnumValue object.

        Arguments:
        value: The initial value the IntEnum should be set to
        lock: Optional `Lock` or `RLock` instance to use for synchronization

        """
        if lock is not None:
            self.lock = lock
        else:
            self.lock = multiprocessing.RLock()

        if isinstance(value, self.EnumType):
            intvalue: int = value
        elif isinstance(value, str):
            intvalue = self.to_value(value)
        else:
            message = "Can not set '{e}' to value of type '{t}'".format(e=self.EnumType, t=type(value))
            raise TypeError(message)

        self._value = multiprocessing.Value("i", intvalue, lock=self.lock)

    def get_lock(self) -> Lock | RLock:
        """Return the lock object used for synchronization."""
        return self._value.get_lock()

    def set(self, value: T | str) -> None:
        """Set the IntEnum to the given value."""
        if isinstance(value, self.EnumType):
            self._value.value = value
        elif isinstance(value, str):
            self._value.value = self.to_value(value)
        else:
            message = "Can not set '{e}' to value of type '{t}'".format(e=self.EnumType, t=type(value))
            raise TypeError(message)

    @property
    def value(self) -> T:
        """The value given to the IntEnum member."""
        return self._value.value  # type: ignore[no-any-return]

    @value.setter
    def value(self, value: T | str) -> None:
        self.set(value)

    @property
    def name(self) -> str:
        """The name used to define the Enum member."""
        return self.from_value(self._value.value)

    def __eq__(self, other: object) -> Any:  # noqa: D105
        if isinstance(other, IntEnumValue):
            if self.EnumType == other.EnumType:
                return self._value.value == other._value.value
            else:
                message = "Can not compare '{e}' to '{t}'".format(e=self.EnumType, t=other.EnumType)
                raise TypeError(message)
        elif isinstance(other, (self.EnumType, int)):
            return self._value.value == other
        elif isinstance(other, str):
            return self._value.value == self.to_value(other)
        else:
            message = "Can not compare '{e}' to '{t}'".format(e=self.EnumType, t=type(other))
            raise TypeError(message)

    # implement __hash__ as implemting __eq__ does away with the default
    def __hash__(self) -> int:  # noqa: D105
        return hash((self.EnumType, self._value.value))

    def to_value(self, name: str) -> int:
        """Return the value given to the IntEnum member."""
        return self.EnumType[name]

    def from_value(self, value: int) -> str:
        """Return the name used to define the IntEnum member."""
        return self.EnumType(value).name
