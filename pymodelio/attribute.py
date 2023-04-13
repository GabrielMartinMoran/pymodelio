from typing import Generic, Callable, Optional, Any, TypeVar, Type

from pymodelio.validators.validator import Validator

T = TypeVar('T')


class GenericAttribute(Generic[T]):

    def __init__(self, validator: Optional[Validator] = None, initable: bool = True,
                 default_factory: Callable = None) -> None:
        self._validator = validator
        self._initable = initable
        self._default_factory = default_factory or (lambda: None)

    def validate(self, value: Optional[Any], path: str) -> None:
        if self.validator is not None:
            self.validator.validate(value, path)

    @property
    def validator(self) -> Validator:
        return self._validator

    @property
    def initable(self) -> bool:
        return self._initable

    @property
    def default_factory(self) -> Callable:
        return self._default_factory

    @property
    def attr_type(self) -> Type:
        return self.__orig_class__.__args__[0]

    def __getitem__(self, attr_type: T) -> Callable[..., T]:
        # Only declared for type hinting
        raise NotImplementedError()


# Indirections for type hinting
class _AttributeRetriever(GenericAttribute):
    def __getitem__(self, attr_type: T) -> Callable[..., T]:
        return GenericAttribute[attr_type]


PymodelioAttribute = _AttributeRetriever()

# Exposed Attribute and aliases
"""
Any of these exposed attributes can be called using this signature:

Attribute(validator: Optional[Validator] = None, initable: bool = True, default_factory: Callable = None)

"""
Attribute: GenericAttribute = PymodelioAttribute
Attr: GenericAttribute = PymodelioAttribute
ModelAttribute: GenericAttribute = PymodelioAttribute
ModelAttr: GenericAttribute = PymodelioAttribute
