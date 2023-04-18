import pytest

from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.validators.dict_validator import DictValidator


def test_validate_raises_validation_error_when_provided_value_is_not_instance_of_dict():
    validator = DictValidator()
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate('12345', 'prop')
    assert ex_info.value.args[0] == 'prop is not instance of dict'


def test_validate_does_not_raise_error_when_provided_value_is_instance_of_provided_type():
    validator = DictValidator()
    validator.validate({}, 'path')
