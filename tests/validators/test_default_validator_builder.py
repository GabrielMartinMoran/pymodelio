from datetime import datetime
from typing import Optional, List, Set, Tuple, Any, Dict, Union, ForwardRef

import pytest

from pymodelio import PymodelioModel, Attr
from pymodelio.exceptions import AutoValidatorCreationException
from pymodelio.validators import StringValidator, BoolValidator, IntValidator, FloatValidator, DictValidator, \
    ListValidator, SetValidator, TupleValidator, DatetimeValidator, Validator, ForwardRefValidator
from pymodelio.validators.default_validators_builder import DefaultValidatorsBuilder


def test_build_generates_validator_for_provided_type_if_that_type_is_configured():
    class TestPymodelioModel(PymodelioModel):
        name: Attr(str)

    class NonPymodelioClass:
        name: str

    configured_validators_map = {
        str: StringValidator,
        bool: BoolValidator,
        int: IntValidator,
        float: FloatValidator,
        dict: DictValidator,
        list: ListValidator,
        set: SetValidator,
        tuple: TupleValidator,
        datetime: DatetimeValidator,
        Dict: DictValidator,
        Any: Validator,
        List: ListValidator,
        Tuple: TupleValidator,
        Set: SetValidator,
        TestPymodelioModel: Validator,
    }

    # Non optionals
    for _type, validator_class in configured_validators_map.items():
        validator = DefaultValidatorsBuilder.build(_type)
        assert isinstance(validator, validator_class)
        assert not validator.nullable

    # Optionals
    for _type, validator_class in configured_validators_map.items():
        validator = DefaultValidatorsBuilder.build(Optional[_type])
        assert isinstance(validator, validator_class)
        assert validator.nullable

    # List
    for _type, validator_class in configured_validators_map.items():
        validator = DefaultValidatorsBuilder.build(List[_type])
        assert isinstance(validator, ListValidator)
        assert validator.elements_type == (_type,)
        assert not validator.nullable

    # Set
    for _type, validator_class in configured_validators_map.items():
        validator = DefaultValidatorsBuilder.build(Set[_type])
        assert isinstance(validator, SetValidator)
        assert validator.elements_type == (_type,)
        assert not validator.nullable

    # Tuple
    for _type, validator_class in configured_validators_map.items():
        validator = DefaultValidatorsBuilder.build(Tuple[_type])
        assert isinstance(validator, TupleValidator)
        assert validator.elements_type == (_type,)
        assert not validator.nullable

    # Dict
    for _type, validator_class in configured_validators_map.items():
        validator = DefaultValidatorsBuilder.build(Dict[_type, _type])
        assert isinstance(validator, DictValidator)
        assert not validator.nullable

    # Union
    validator = DefaultValidatorsBuilder.build(Union[str, int, dict])
    assert isinstance(validator, Validator)
    assert validator._expected_types == (str, int, dict)
    assert not validator.nullable

    validator = DefaultValidatorsBuilder.build(Union[str, int, dict, None])
    assert isinstance(validator, Validator)
    assert validator._expected_types == (str, int, dict)
    assert validator.nullable

    # Forwarded references
    validator = DefaultValidatorsBuilder.build('TestPymodelioModel')
    assert isinstance(validator, ForwardRefValidator)
    assert validator._expected_types == (ForwardRef,)
    assert not validator.nullable
    #   After validation, the forwarded reference is corrected
    validator.validate(TestPymodelioModel(name='name'))
    assert validator._expected_types == (TestPymodelioModel,)

    # Non pymodelio classes
    validator = DefaultValidatorsBuilder.build(NonPymodelioClass)
    assert isinstance(validator, Validator)
    assert validator._expected_types == (NonPymodelioClass,)
    assert not validator.nullable


def test_build_raises_error_when_auto_generation_is_too_complex():
    TYPES_TO_TEST = [
        List[Optional[Any]],
        Set[Optional[Any]],
        Tuple[Optional[Any]]
    ]

    EXPECTED_MESSAGES = [
        'Can not automatically instantiate a validator for type typing.List when its elements_type attribute contains typing.Optional',
        'Can not automatically instantiate a validator for type typing.Set when its elements_type attribute contains typing.Optional',
        'Can not automatically instantiate a validator for type typing.Tuple when its elements_type attribute contains typing.Optional',
    ]

    for _type, message in zip(TYPES_TO_TEST, EXPECTED_MESSAGES):
        with pytest.raises(AutoValidatorCreationException) as ex_info:
            DefaultValidatorsBuilder.build(_type)
        assert ex_info.value.args[0] == message
