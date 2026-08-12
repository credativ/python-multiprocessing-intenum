import enum
import multiprocessing
from enum import IntEnum
from unittest import TestCase

from multiprocessing_intenum import IntEnumValue


class FooEnum(IntEnum):
    FOO = enum.auto()
    BAZ = enum.auto()


class Foo(IntEnumValue[FooEnum]):
    pass


class BarEnum(IntEnum):
    BAR = enum.auto()
    QUX = enum.auto()


class Bar(IntEnumValue[BarEnum]):
    pass


class TestMixin:
    pass


class MixedFoo(TestMixin, IntEnumValue[FooEnum]):
    pass


class IntEnumValueTestCase(TestCase):
    def test_init(self) -> None:
        foo = Foo(FooEnum.FOO)
        self.assertEqual(foo, FooEnum.FOO)

    def test_init_no_specific_type(self) -> None:
        class Baz(IntEnumValue):
            pass

        self.assertEqual(Baz.EnumType, IntEnum)  # type: ignore[misc]

    def test_init_subsubclass(self) -> None:
        class Baz(Bar[BarEnum]):
            pass

        self.assertEqual(Baz.EnumType, BarEnum)  # type: ignore[misc]

    def test_init_subsubclass_no_specific_type(self) -> None:
        class Baz(Bar):
            pass

        self.assertEqual(Baz.EnumType, BarEnum)  # type: ignore[misc]

    def test_init_mixin(self) -> None:
        foo = MixedFoo(FooEnum.FOO)
        self.assertEqual(foo, FooEnum.FOO)

    def test_init_multi_inheritance_mro(self) -> None:
        class FooOrBar(Foo, Bar):
            pass

        self.assertEqual(FooOrBar.EnumType, FooEnum)  # type: ignore[misc]

    def test_init_multi_inheritance_mro_generic(self) -> None:
        class FooOrBar(Foo, IntEnumValue[BarEnum]):
            pass

        self.assertEqual(FooOrBar.EnumType, FooEnum)  # type: ignore[misc]

    def test_init_name(self) -> None:
        foo = Foo(FooEnum.FOO.name)
        self.assertEqual(foo, FooEnum.FOO)

    def test_init_typing(self) -> None:
        with self.assertRaises(TypeError):
            foo = Foo(BarEnum.BAR)  # type: ignore[arg-type] # noqa: F841

    def test_init_lock_individual(self) -> None:
        foo = Foo(FooEnum.FOO)
        bar = Bar(BarEnum.BAR)
        self.assertNotEqual(foo.get_lock(), bar.get_lock())

    def test_init_lock_shared(self) -> None:
        testlock = multiprocessing.RLock()
        foo = Foo(FooEnum.FOO, testlock)
        bar = Bar(BarEnum.BAR, testlock)
        self.assertEqual(foo.get_lock(), testlock)
        self.assertEqual(foo.get_lock(), bar.get_lock())

    def test_setter(self) -> None:
        foo = Foo(FooEnum.FOO)
        foo.value = FooEnum.BAZ
        self.assertEqual(foo, FooEnum.BAZ)

    def test_setter_name(self) -> None:
        foo = Foo(FooEnum.FOO)
        foo.value = FooEnum.BAZ.name
        self.assertEqual(foo, FooEnum.BAZ)

    def test_setter_typing(self) -> None:
        foo = Foo(FooEnum.FOO)
        with self.assertRaises(TypeError):
            foo.value = BarEnum.BAR  # type: ignore[assignment]

    def test_property(self) -> None:
        foo = Foo(FooEnum.FOO)
        self.assertEqual(foo.value, FooEnum.FOO)
        foo.value = FooEnum.BAZ
        self.assertEqual(foo.value, FooEnum.BAZ)

    def test_property_name(self) -> None:
        foo = Foo(FooEnum.FOO)
        self.assertEqual(foo.name, FooEnum.FOO.name)
        foo.value = FooEnum.BAZ
        self.assertEqual(foo.name, FooEnum.BAZ.name)

    def test_getter(self) -> None:
        foo = Foo(FooEnum.FOO)
        self.assertEqual(foo, FooEnum.FOO)
        foo.value = FooEnum.BAZ
        self.assertEqual(foo, FooEnum.BAZ)

    def test_eq(self) -> None:
        foo1 = Foo(FooEnum.FOO)
        foo2 = Foo(FooEnum.FOO)
        self.assertEqual(foo1, foo2)

    def test_eq_enum(self) -> None:
        foo = Foo(FooEnum.FOO)
        self.assertEqual(foo, FooEnum.FOO)

    def test_eq_str(self) -> None:
        foo = Foo(FooEnum.FOO)
        self.assertEqual(foo, FooEnum.FOO.name)

    def test_eq_typing_intenumvalue(self) -> None:
        foo = Foo(FooEnum.FOO)
        bar = Bar(BarEnum.BAR)
        with self.assertRaises(TypeError):
            foo == bar  # noqa: B015

    def test_eq_typing_float(self) -> None:
        foo = Foo(FooEnum.FOO)
        x = 1.8
        with self.assertRaises(TypeError):
            foo == x  # noqa: B015

    def test_hash(self) -> None:
        foo1 = Foo(FooEnum.FOO)
        foo2 = Foo(FooEnum.FOO)
        self.assertEqual(hash(foo1), hash(foo2))

    def test_hash_value(self) -> None:
        foo1 = Foo(FooEnum.FOO)
        foo2 = Foo(FooEnum.BAZ)
        self.assertNotEqual(hash(foo1), hash(foo2))

    def test_hash_type(self) -> None:
        foo = Foo(FooEnum.FOO)
        bar = Bar(BarEnum.BAR)
        self.assertNotEqual(hash(foo), hash(bar))
