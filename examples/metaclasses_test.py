import timeit

from pymodelio import Attr
from pymodelio.attribute import PymodelioAttr


def _get_annotations(cls: type) -> dict:
    annotations = cls.__annotations__ if hasattr(cls, '__annotations__') else {}
    for parent in cls.__bases__:
        if hasattr(parent, '__annotations__'):
            annotations = {**annotations, **parent.__annotations__}
    return annotations


def _get_model_attrs(cls: type) -> dict:
    validated_attrs = {}
    annotations = _get_annotations(cls)
    for k in annotations:
        v = annotations[k]
        if isinstance(v, PymodelioAttr):
            validated_attrs[k] = v
    return validated_attrs


class PymodelioMetaclass(type):

    def __call__(pmcls, *args, use_slots: bool = False, **kwargs):
        print('call', pmcls, args, kwargs)

        if getattr(pmcls, '__pymodelio_model__', False):
            return super().__call__(*args, **kwargs)

        model_attrs = _get_model_attrs(pmcls)

        inner_dict = {
            '__pymodelio_model__': True,
            '__model_attrs__': model_attrs
        }

        if use_slots:
            inner_dict['__slots__'] = tuple(model_attrs.keys())

        inner_class = type(pmcls.__name__, (pmcls,), inner_dict)

        """

        class _Inner(pmcls):
            __pymodelio_model__ = True
            __model_attrs__ = model_attrs
            __slots__ = tuple(model_attrs.keys())
        """

        return inner_class(*args, **kwargs)


class PymodelioBaseClass(metaclass=PymodelioMetaclass):
    __slots__ = ('_protected_attr',)

    def __init__(self, *args, auto_validate: bool = True, **kwargs) -> None:
        pass


class A(PymodelioBaseClass):
    _protected_attr: Attr(str)
    __private_attr: Attr(str)


class B(A):
    public_attr: Attr(str)

    def calc(self) -> None:
        self.public_attr = 'ASD'
        _ = self.public_attr


b = B(public_attr='1', protected_attr='2', private_attr='3')
print(f'{dir(b) = }')
print(f'{b.__class__.__name__ = }')
print(f'{b.__slots__ = }')
b.custom_attr_for_b = 'Ups...'
print(f'{b.__dict__ = }')

non_slotted_b = B(public_attr='1', protected_attr='2', private_attr='3', use_slots=False)
slotted_b = B(public_attr='1', protected_attr='2', private_attr='3', use_slots=True)

print(f'Non slotted B: {timeit.timeit(non_slotted_b.calc, number=50_000_000)}')
print(f'Slotted B: {timeit.timeit(slotted_b.calc, number=50_000_000)}')

"""


class Slotted:
    __slots__ = ('attr',)

    def __init__(self, attr: str) -> None:
        self.attr = attr


s = Slotted('Hello world!')
s.custom_attr_for_slotted = 1234

"""
