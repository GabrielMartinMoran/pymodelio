import pytest

from src.exceptions.model_validation_exception import ModelValidationException
from src.validators.numeric_validator import NumericValidator


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = NumericValidator(expected_type=int, nullable=True)
    validator.validate(None, 'path')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = NumericValidator(expected_type=int, nullable=False)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_when_provided_value_is_not_provided_type():
    validator = NumericValidator(expected_type=int)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('12345', 'prop')
    assert ex_info.value.args[0] == 'prop is not a valid int'


def test_validate_raises_validation_error_when_provided_value_is_lower_than_min():
    validator = NumericValidator(expected_type=int, min_value=10)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(9, 'prop')
    assert ex_info.value.args[0] == 'prop is lower than 10'


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_value_is_greater_than_min():
    validator = NumericValidator(expected_type=int, min_value=9)
    validator.validate(10, 'path')


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_value_is_equal_to_min():
    validator = NumericValidator(expected_type=int, min_value=10)
    validator.validate(10, 'path')


def test_validate_raises_validation_error_when_provided_value_is_greater_than_max():
    validator = NumericValidator(expected_type=int, max_value=10)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(11, 'prop')
    assert ex_info.value.args[0] == 'prop is greater than 10'


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_value_is_lower_than_max():
    validator = NumericValidator(expected_type=int, max_value=10)
    validator.validate(9, 'path')


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_value_is_equal_to_max():
    validator = NumericValidator(expected_type=int, max_value=10)
    validator.validate(10, 'path')
