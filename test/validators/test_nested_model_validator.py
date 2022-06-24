import datetime

import pytest

from src.attribute import Attribute
from src.exceptions.model_validation_exception import ModelValidationException
from src.model import pymodelio_model
from src.validators.datetime_validator import DatetimeValidator
from src.validators.nested_model_validator import NestedModelValidator


def test_validate_does_not_raise_error_when_provided_value_is_none_and_property_is_nullable():
    validator = NestedModelValidator(nullable=True)
    validator.validate(None, '')


def test_validate_raises_validation_error_when_provided_value_is_none_and_property_is_not_nullable():
    validator = NestedModelValidator(nullable=False)
    with pytest.raises(ModelValidationException) as ex_info:
        validator.validate(None, 'prop')
    assert ex_info.value.args[0] == 'prop must not be None'


def test_validate_raises_validation_error_when_provided_value_does_not_implement_validate_method():
    class NoModelClass:
        pass

    validator = NestedModelValidator()
    with pytest.raises(NotImplementedError) as ex_info:
        validator.validate(NoModelClass(), 'prop')
    assert ex_info.value.args[0] == 'NoModelClass model does not implement validate method'


def test_validate_does_not_raise_error_when_provided_value_is_valid():
    @pymodelio_model
    class ModelClass:
        name: Attribute[str]()

    validator = NestedModelValidator()
    validator.validate(ModelClass(name='test'), 'path')
