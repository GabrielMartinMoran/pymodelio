import typing
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, _SpecialForm

from pymodelio.exceptions import AutoValidatorCreationException
from pymodelio.validators import Validator, StringValidator, FloatValidator, IntValidator, BoolValidator, \
    DictValidator, ListValidator, DatetimeValidator, SetValidator, TupleValidator
from pymodelio.validators.forward_ref_validator import ForwardRefValidator


def _generate_validators_mapping() -> dict:
    return {
        str: StringValidator,
        bool: BoolValidator,
        int: IntValidator,
        float: FloatValidator,
        dict: DictValidator,
        list: ListValidator,
        set: SetValidator,
        tuple: TupleValidator,
        datetime: DatetimeValidator,
        typing.Dict: DictValidator,
        typing.List: ListValidator,
        typing.Tuple: TupleValidator,
        typing.Set: SetValidator,
        typing.Any: Validator
    }


@dataclass
class _DestructuredType:
    outer: typing.Union[type, _SpecialForm]
    outer_nullable: bool = field(default_factory=lambda: False)
    inners: typing.List['_DestructuredType'] = field(default_factory=list)

    def is_plain(self) -> bool:
        return len(self.inners) == 0


class DefaultValidatorsBuilder:
    _VALIDATORS_MAPPING = _generate_validators_mapping()

    @classmethod
    def build(cls, attr_type: type) -> Optional[Validator]:
        destructured = cls._destructurate(attr_type)
        return cls._instantiate_from_destructured(destructured)

    @classmethod
    def _destructurate(cls, attr_type: type) -> _DestructuredType:  # noqa: C901
        if attr_type in cls._VALIDATORS_MAPPING or (
                hasattr(attr_type, '_is_pymodelio_model') and attr_type._is_pymodelio_model()):
            return _DestructuredType(outer=attr_type)
        if attr_type == typing.Any:
            return _DestructuredType(outer=typing.Any)
        # typing.ForwardRef
        if isinstance(attr_type, typing.ForwardRef):
            return _DestructuredType(outer=typing.ForwardRef, inners=[attr_type])
        if isinstance(attr_type, str):
            return _DestructuredType(outer=typing.ForwardRef, inners=[typing.ForwardRef(attr_type)])
        # other typings
        if attr_type.__module__ == 'typing' and hasattr(attr_type, '__reduce__'):
            reduced = attr_type.__reduce__()[1]
            if len(reduced) == 1:
                return _DestructuredType(outer=reduced[0])
            _type, args = reduced
            if _type == typing.Union:
                # Optional
                if len(args) == 2 and type(None) in args:
                    return _DestructuredType(outer=typing.Optional, outer_nullable=True, inners=[
                        cls._destructurate(x) for x in args if x != type(None)  # noqa: E721
                    ])
                # Union
                else:
                    is_nullable = False
                    inners = []
                    for x in args:
                        if x == type(None):  # noqa: E721
                            is_nullable = True
                        else:
                            inners.append(cls._destructurate(x))
                    return _DestructuredType(outer=typing.Union, outer_nullable=is_nullable, inners=inners)
            if _type in (typing.List, typing.Tuple, typing.Set):
                return _DestructuredType(outer=_type, outer_nullable=True, inners=[cls._destructurate(args)])
            if _type == typing.Dict:
                return _DestructuredType(outer=dict)
        return _DestructuredType(outer=attr_type)

    @classmethod
    def _instantiate_from_destructured(cls, destructured: _DestructuredType, nullable: bool = False) -> Validator:
        if destructured.is_plain():
            return cls._instantiate_validator(destructured.outer, nullable)
        if destructured.outer == typing.ForwardRef:
            return ForwardRefValidator(ref=destructured.inners[0], nullable=nullable)
        if destructured.outer == typing.Optional:
            # TODO: Define limitations
            return cls._instantiate_from_destructured(destructured.inners[0], nullable=True)
        if destructured.outer == typing.Union:
            return Validator(expected_type=[x.outer for x in destructured.inners], nullable=destructured.outer_nullable)
        if destructured.outer in (typing.List, typing.Set, typing.Tuple):
            return cls._instantiate_iterable(
                destructured.outer,
                destructured.inners[0].outer if destructured.inners else None,
                nullable
            )
        return Validator(nullable=nullable)

    @classmethod
    def _instantiate_iterable(cls, special_form: _SpecialForm, elements_type: type, nullable: bool) -> Validator:
        if elements_type in (typing.Optional,):
            raise AutoValidatorCreationException(
                f'Can not automatically instantiate a validator for type {str(special_form)} '
                f'when its elements_type attribute contains {elements_type}'
            )
        validator_class = cls._VALIDATORS_MAPPING[special_form]
        return validator_class(elements_type=elements_type, nullable=nullable)

    @classmethod
    def _instantiate_validator(cls, class_type: type, nullable: bool) -> Validator:
        if class_type in cls._VALIDATORS_MAPPING:
            return cls._VALIDATORS_MAPPING[class_type](nullable=nullable)
        return Validator(expected_type=class_type, nullable=nullable)
