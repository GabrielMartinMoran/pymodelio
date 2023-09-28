from typing import Callable, Optional, Any, TypeVar, Union, Tuple, Iterable

from pymodelio import UNDEFINED, PymodelioSettings, PymodelioSetting
from pymodelio.undefined import Undefined
from pymodelio.validators.default_validators_builder import DefaultValidatorsBuilder
from pymodelio.validators.validator import Validator

T = TypeVar('T')


class PymodelioAttr:
    __slots__ = (
        '_attr_type', '_initable', '_default_factory', '_init_aliases', '_validator', '_compare'
    )

    @classmethod
    def _default_factory_function(cls) -> None:
        return None

    def __init__(self, attr_type: T, validator: Optional[Validator] = UNDEFINED, initable: bool = True,
                 init_alias: Optional[str] = None, init_aliases: Optional[Iterable[str]] = None,
                 default_factory: Callable = None, compare: bool = True) -> None:
        self._attr_type = attr_type
        self._init_attr_aliases(init_alias, init_aliases)
        self._initable = initable or len(self._init_aliases) > 0
        self._default_factory = default_factory if default_factory is not None else self._default_factory_function
        self._init_validator(validator)
        self._compare = compare

    def _init_attr_aliases(self, init_alias: Optional[str], init_aliases: Optional[Iterable[str]]) -> None:
        if init_aliases is not None:
            self._init_aliases = tuple(init_aliases)
        elif init_alias is not None:
            self._init_aliases = (init_alias,)
        else:
            self._init_aliases = tuple()

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

    @property
    def init_aliases(self) -> Tuple[str]:
        return self._init_aliases

    @property
    def compare(self) -> bool:
        return self._compare


def Attr(attr_type: T, /, *, validator: Optional[Validator] = UNDEFINED, initable: bool = True,
         init_alias: Optional[str] = None, init_aliases: Iterable[str] = None, default_factory: Callable = None,
         compare: bool = True) -> T:
    return PymodelioAttr(attr_type=attr_type, validator=validator, initable=initable, init_alias=init_alias,
                         init_aliases=init_aliases, default_factory=default_factory, compare=compare)
