import pytest

import pymodelio
from pymodelio.attribute import Attribute
from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators.validator import Validator


def test_validate_does_not_raise_error_when_provided_value_is_not_none():
    validator = Validator(nullable=False)
    validator.validate('Not None', '')


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = Validator(nullable=True)
    validator.validate('prop_to_validate', '')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = Validator()
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_with_custom_message_when_provided_value_is_not_valid_and_message_was_set():
    validator = Validator(message='is not valid')
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop is not valid'


def test_validate_does_not_raise_error_when_provided_value_is_instance_of_expected_type():
    validator = Validator(expected_type=str)
    validator.validate('Not None', '')


def test_validate_does_not_raise_error_when_provided_value_is_a_model_and_is_valid():
    @pymodelio.model
    class ModelClass:
        name: Attribute[str](Validator(expected_type=str))

    validator = Validator(expected_type=ModelClass)
    validator.validate(ModelClass(name='tests'), 'path')


def test_validate_raises_validation_error_when_provided_value_is_a_model_and_it_is_not_valid():
    @pymodelio.model
    class ModelClass:
        name: Attribute[str](Validator(expected_type=[str]))

    validator = Validator(expected_type=ModelClass)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(ModelClass(name=12345, auto_validate=False), 'path')
    assert ex_info.value.args[0] == 'path.name is not a valid str'
