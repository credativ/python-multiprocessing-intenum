"""A multiprocessing safe shared object for `IntEnum` enum values."""

import multiprocessing
from enum import IntEnum
from multiprocessing.synchronize import Lock, RLock
from typing import Any, Generic, TypeVar, get_args

from ._version import version as __version__  # noqa: F401

T = TypeVar("T", bound=IntEnum)


class IntEnumValue(Generic[T]):
    """A multiprocessing safe shared object for `IntEnum` enum values."""

    # Pre-initialize type here to avoid numerous type ignores elsewhere
    EnumType: type[T | IntEnum] = IntEnum

    @classmethod
    def __init_subclass__(cls) -> None:  # noqa: D105
        # set EnumType to the specific type specified by subclass
        orig_base = cls.__orig_bases__[0]  # type: ignore[attr-defined]
        cls.EnumType = get_args(orig_base)[0]

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
