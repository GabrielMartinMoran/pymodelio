# Creating a custom validator and using it
from typing import List, Optional, Any

from pymodelio import Attr, PymodelioModel
from pymodelio.exceptions import ModelValidationException
from pymodelio.validators import Validator


class SpecificStringValidator(Validator):

    def __init__(self, possible_values: List[Any], nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=str, nullable=nullable, message=message)
        self._possible_values = possible_values

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if value not in self._possible_values:
            self._raise_validation_error(path, f'must be one of {self._possible_values}')


class CustomModel(PymodelioModel):
    attr: Attr(str, validator=SpecificStringValidator(possible_values=['A', 'B', 'C']))


try:
    instance = CustomModel(attr='D')
except ModelValidationException as e:
    print(e)
    # > CustomModel.attr must be one of ['A', 'B', 'C']
