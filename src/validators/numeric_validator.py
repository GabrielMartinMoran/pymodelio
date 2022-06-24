import math
from typing import Any

from src.exceptions.model_validation_exception import ModelValidationException
from src.validators.validator import Validator


class NumericValidator(Validator):

    def __init__(self, expected_type, min_value=-math.inf, max_value=math.inf, **kwargs) -> None:
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.expected_type = expected_type

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if not isinstance(value, self.expected_type):
            self.raise_validation_error(path, f'is not a valid {self.expected_type.__name__}')
        if value < self.min_value:
            self.raise_validation_error(path, f'is lower than {self.min_value}')
        if value > self.max_value:
            self.raise_validation_error(path, f'is greater than {self.max_value}')
