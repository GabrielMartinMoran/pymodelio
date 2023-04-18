from typing import Callable, Optional, Any, TypeVar, Union

from pymodelio import UNDEFINED, PymodelioSettings, PymodelioSetting
from pymodelio.undefined import Undefined
from pymodelio.validators.default_validators_builder import DefaultValidatorsBuilder
from pymodelio.validators.validator import Validator

T = TypeVar('T')


class PymodelioAttr:
    def __init__(self, attr_type: T, validator: Optional[Validator] = UNDEFINED, initable: bool = True,
                 default_factory: Callable = None) -> None:
        self._attr_type = attr_type
        self._initable = initable
        self._default_factory = default_factory or (lambda: None)
        self._init_validator(validator)

    def _init_validator(self, validator: Union[Validator, None, Undefined]) -> None:
        if validator == UNDEFINED:
            if PymodelioSettings.get(PymodelioSetting.USE_DEFAULT_ATTR_VALIDATOR_IF_NOT_DEFINED):
                self._validator = DefaultValidatorsBuilder.build(self.attr_type)
            else:
                self._validator = None
        else:
            self._validator = validator

    def validate(self, value: Optional[Any], path: str) -> None:
        if self.validator is not None:
            self.validator.validate(value, path)

    @property
    def validator(self) -> Optional[Validator]:
        return self._validator

    @property
    def initable(self) -> bool:
        return self._initable

    @property
    def default_factory(self) -> Callable:
        return self._default_factory

    @property
    def attr_type(self) -> T:
        return self._attr_type


def Attr(attr_type: T, validator: Optional[Validator] = UNDEFINED, initable: bool = True,
         default_factory: Callable = None) -> T:
    return PymodelioAttr(attr_type=attr_type, validator=validator, initable=initable,
                         default_factory=default_factory)
