# Customizing validation process by implementing `__when_validating_an_attr__`
from typing import Any

from pymodelio import Attr, PymodelioModel
from pymodelio.attribute import PymodelioAttr
from pymodelio.exceptions import ModelValidationException


class CustomModel(PymodelioModel):
    name: Attr(str)  # As we haven't specified a validator, a StringValidator is inferred
    age: Attr(str, validator=None)

    def __when_validating_an_attr__(self, attr_name: str, attr_value: Any, attr_path: str,
                                    parent_path: str, attr: PymodelioAttr) -> None:
        # As this is called after name validator is called, we know that name is a string
        if attr_name == 'name' and len(attr_value) == 0:
            raise ModelValidationException(f'{attr_path} must not be blank')
        if attr_name == 'age' and attr_value < 0:
            raise ModelValidationException(f'{attr_path} must not be less than zero')


try:
    instance = CustomModel(name='', age=70)
except ModelValidationException as e:
    print(e)
    # > CustomModel.name must not be blank

try:
    instance = CustomModel(name='Rick Sanchez', age=-1)
except ModelValidationException as e:
    print(e)
    # > CustomModel.age must not be less than zero
