from typing import Generic, Callable, Optional, Any, Type, TypeVar

from src.validators.validator import Validator

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

    """
    def validate(self, value: Optional[Any], path: str) -> None:
        if not self.is_valid(value):
            raise ModelValidationException(f'Validation exception on {path}')
        if isinstance(value, base_model.BaseModel):
            return value.validate(path=path)
        if isinstance(value, (list, set, tuple)):
            self._validate_iterable(value, path=path)
    """

    """
    @classmethod
    def _validate_iterable(cls, value: Iterable, path: str) -> None:
        for x in value:
            # TODO: Validate primitive types
            if isinstance(x, base_model.BaseModel):
                return x.validate(path=path)
    """

    """
    def is_valid(self, value: Optional[Any]) -> bool:
        if value is None:
            return self._nullable
        if hasattr(self.attr_type, '__origin__') and self.attr_type.__origin__ in [list, set, tuple]:
            return isinstance(value, self.attr_type.__origin__)
        elif not isinstance(value, self.attr_type):
            return False
        return True
    """

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
