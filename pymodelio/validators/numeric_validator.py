from numbers import Number
from typing import Any, Union, List, Optional

from pymodelio.validators.validator import Validator


class NumericValidator(Validator):

    def __init__(self, min_value: Optional[Number] = None, max_value: Optional[Number] = None,
                 expected_type: Union[type, List[type]] = None, nullable: bool = False,
                 message: Optional[str] = None) -> None:
        super().__init__(expected_type=expected_type, nullable=nullable, message=message)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if self.min_value is not None and value < self.min_value:
            self.raise_validation_error(path, f'is lower than {self.min_value}')
        if self.max_value is not None and value > self.max_value:
            self.raise_validation_error(path, f'is greater than {self.max_value}')
