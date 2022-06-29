import pytest

from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators.list_validator import ListValidator


def test_validate_does_not_raise_error_when_provided_value_is_valid():
    validator = ListValidator(elements_type=int)
    validator.validate([1, 2, 3, 4, 5], '')


def test_validate_raises_validation_error_when_provided_value_is_not_a_list():
    validator = ListValidator(elements_type=int)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(set(), 'prop')
    assert ex_info.value.args[0] == 'prop is not a valid list'
