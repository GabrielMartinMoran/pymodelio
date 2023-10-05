from typing import Callable, Optional, Any, TypeVar, Union, Iterable

from pymodelio import UNDEFINED, PymodelioSettings, PymodelioSetting
from pymodelio.undefined import Undefined
from pymodelio.validators.default_validators_builder import DefaultValidatorsBuilder
from pymodelio.validators.validator import Validator

T = TypeVar('T')


class PymodelioAttr:
    __slots__ = (
        'attr_type', 'attr_type_origin', 'initable', 'default_factory', 'init_aliases', 'validator', 'compare',
        '_initialized'
    )

    def __init__(self, attr_type: T, validator: Optional[Validator] = UNDEFINED, initable: bool = True,
                 init_alias: Optional[str] = None, init_aliases: Optional[Iterable[str]] = None,
                 default_factory: Optional[Callable] = None, compare: bool = True) -> None:
        self.attr_type = attr_type
        self.attr_type_origin = getattr(attr_type, '__origin__', attr_type)
        self._init_attr_aliases(init_alias, init_aliases)
        self.initable = initable or len(self.init_aliases) > 0
        self.default_factory = default_factory
        self._init_validator(validator)
        self.compare = compare
        self._initialized = True

    def _init_attr_aliases(self, init_alias: Optional[str], init_aliases: Optional[Iterable[str]]) -> None:
        if init_aliases is not None:
            self.init_aliases = tuple(init_aliases)
        elif init_alias is not None:
            self.init_aliases = (init_alias,)
        else:
            self.init_aliases = tuple()

    def _init_validator(self, validator: Union[Validator, None, Undefined]) -> None:
        if validator == UNDEFINED:
            if PymodelioSettings.get(PymodelioSetting.USE_DEFAULT_ATTR_VALIDATOR_IF_NOT_DEFINED):
                self.validator = DefaultValidatorsBuilder.build(self.attr_type)
            else:
                self.validator = None
        else:
            self.validator = validator

    def validate(self, value: Optional[Any], path: str) -> None:
        if self.validator is not None:
            self.validator.validate(value, path)

    def __setattr__(self, key, value) -> None:
        if getattr(self, '_initialized', False):
            raise RuntimeError('Pymodelio Attributes descriptors can not be modified once instantiated')
        super().__setattr__(key, value)


def Attr(attr_type: T, /, *, validator: Optional[Validator] = UNDEFINED, initable: bool = True,
         init_alias: Optional[str] = None, init_aliases: Iterable[str] = None,
         default_factory: Optional[Callable] = None, compare: bool = True) -> T:
    return PymodelioAttr(attr_type=attr_type, validator=validator, initable=initable, init_alias=init_alias,
                         init_aliases=init_aliases, default_factory=default_factory, compare=compare)
