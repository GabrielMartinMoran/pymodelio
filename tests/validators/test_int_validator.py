import pytest

from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators.int_validator import IntValidator


def test_validate_raises_validation_error_when_provided_value_is_not_int():
    validator = IntValidator()
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('12345', 'prop')
    assert ex_info.value.args[0] == 'prop is not instance of int'


def test_validate_does_not_raise_error_when_provided_value_is_valid():
    validator = IntValidator()
    validator.validate(10, 'path')
