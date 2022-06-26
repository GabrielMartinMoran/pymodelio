import datetime

import pytest

from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators.datetime_validator import DatetimeValidator


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = DatetimeValidator(nullable=True)
    validator.validate(None, '')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = DatetimeValidator(nullable=False)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_when_provided_value_is_not_a_datetime():
    validator = DatetimeValidator()
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('12345', 'prop')
    assert ex_info.value.args[0] == 'prop is not a valid datetime'


def test_validate_does_not_raise_error_when_provided_value_is_valid():
    validator = DatetimeValidator()
    validator.validate(datetime.datetime.now(), 'path')
