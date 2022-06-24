import pytest

from src.exceptions.model_validation_exception import ModelValidationException
from src.validators.float_validator import FloatValidator


def test_validate_raises_validation_error_when_provided_value_is_not_float():
    validator = FloatValidator()
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('12345', 'prop')
    assert ex_info.value.args[0] == 'prop is not a valid float'


def test_validate_does_not_raise_error_when_provided_value_is_valid():
    validator = FloatValidator()
    validator.validate(10.0, 'path')
