import pytest

from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators import validation_patterns
from pymodelio.validators.string_validator import StringValidator


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = StringValidator(nullable=True)
    validator.validate(None, '')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = StringValidator(nullable=False)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_when_provided_value_is_not_string():
    validator = StringValidator()
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(12345, 'prop')
    assert ex_info.value.args[0] == 'prop is not a valid str'


def test_validate_raises_validation_error_when_provided_value_length_is_lower_than_min_len():
    validator = StringValidator(min_len=2)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('a', 'prop')
    assert ex_info.value.args[0] == 'prop is shorter than 2'


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_length_is_greater_than_min_len():
    validator = StringValidator(min_len=2)
    validator.validate('abc', 'prop')


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_length_is_equal_to_min_len():
    validator = StringValidator(min_len=2)
    validator.validate('ab', 'prop')


def test_validate_raises_validation_error_when_provided_value_length_is_greater_than_max_len():
    validator = StringValidator(max_len=2)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('abc', 'prop')
    assert ex_info.value.args[0] == 'prop is longer than 2'


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_length_is_lower_than_max_len():
    validator = StringValidator(max_len=2)
    validator.validate('a', 'prop')


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_length_is_equal_to_max_len():
    validator = StringValidator(max_len=2)
    validator.validate('ab', 'prop')


def test_validate_raises_validation_error_when_provided_value_length_is_different_than_fixed_len():
    validator = StringValidator(fixed_len=2)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('abc', 'prop')
    assert ex_info.value.args[0] == 'prop length is different than 2'


def test_validate_does_not_raise_error_when_provided_value_is_valid_and_length_is_equal_to_fixed_len():
    validator = StringValidator(fixed_len=2)
    validator.validate('ab', 'prop')


def test_validate_raises_validation_error_when_provided_value_does_not_match_regex():
    validator = StringValidator(regex=validation_patterns.EMAIL_VALIDATION_PATTERN)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('tests text', 'prop')
    assert ex_info.value.args[0] == 'prop does not match configured regex'


def test_validate_does_not_raise_error_when_property_is_valid_and_value_matches_regex():
    validator = StringValidator(regex=validation_patterns.EMAIL_VALIDATION_PATTERN)
    validator.validate('tests@tests.com', 'prop')
