import pytest

import pymodelio
from pymodelio import PymodelioModel
from pymodelio.attribute import Attr
from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators import IterableValidator, StringValidator


def test_validate_does_not_raise_error_when_provided_value_is_not_none():
    validator = IterableValidator(expected_type=list, nullable=False)
    validator.validate([], '')


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = IterableValidator(expected_type=list, nullable=True)
    validator.validate(None, '')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = IterableValidator(expected_type=list)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_when_provided_value_is_not_an_instance_of_expected_type():
    expected_types = [list, tuple, set]
    for expected_type in expected_types:
        validator = IterableValidator(expected_type=expected_type)
        with pytest.raises(ModelValidationException) as ex_info:
            validator.validate(12345, 'prop')
        assert ex_info.value.args[0] == f'prop is not instance of {expected_type.__name__}'


def test_validate_does_not_raise_error_when_provided_value_is_a_list_of_models_and_all_are_valid():
    class ModelClass(PymodelioModel):
        name: Attr(str)

    expected_types = [list, tuple, set]
    for expected_type in expected_types:
        validator = IterableValidator(expected_type=expected_type, elements_type=ModelClass)
        iterable = expected_type([ModelClass(name='tests')])
        validator.validate(iterable, 'path')


def test_validate_raises_validation_error_when_provided_value_is_a_list_of_models_and_at_least_one_is_not_valid():
    class ModelClass(PymodelioModel):
        name: Attr(str)

    validator = IterableValidator(expected_type=list, elements_type=ModelClass)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate([
            ModelClass(name='12345', auto_validate=False),
            ModelClass(name=12345, auto_validate=False)], 'path')
    assert ex_info.value.args[0] == 'path[1].name is not instance of str'


def test_validate_does_not_raise_error_when_provided_value_is_compounded_of_different_types_and_elements_type_was_not_defined():
    expected_types = [list, tuple, set]
    for expected_type in expected_types:
        validator = IterableValidator(expected_type=expected_type)
        iterable = expected_type([12345, 12345.0, '12345'])
        validator.validate(iterable, 'path')


def test_validate_raises_validation_error_when_provided_value_is_empty_and_empty_values_are_not_allowed():
    expected_types = [list, tuple, set]
    for expected_type in expected_types:
        validator = IterableValidator(expected_type=expected_type, allow_empty=False)
        iterable = expected_type()
        with pytest.raises(ModelValidationException) as ex_info:
            validator.validate(iterable, 'prop')
        assert ex_info.value.args[0] == 'prop must not be empty'
