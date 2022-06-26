from typing import Generic, Callable, Optional, Any, Type, TypeVar

from pymodelio.validators.validator import Validator

T = TypeVar('T')


class Attribute(Generic[T]):
    def __init__(self, validator: Optional[Validator] = None, initable: bool = True,
                 default_factory: Callable = None) -> None:
        self._validator = validator
        self._initable = initable
        self._default_factory = default_factory or (lambda: None)

    def get(self) -> T:
        return self._attr_type

    def validate(self, value: Optional[Any], path: str) -> None:
        if self.validator is not None:
            self.validator.validate(value, path)

    @property
    def attr_type(self) -> Type:
        return self.__orig_class__.__args__[0]

    @property
    def validator(self) -> Validator:
        return self._validator

    @property
    def initable(self) -> bool:
        return self._initable

    @property
    def default_factory(self) -> Callable:
        return self._default_factory


# Aliases of Attribute class
Attr = Attribute
ModelAttribute = Attribute
ModelAttr = Attribute
