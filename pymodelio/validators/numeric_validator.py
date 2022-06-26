import math
from numbers import Number
from typing import Any

from pymodelio.validators.validator import Validator


class NumericValidator(Validator):

    def __init__(self, min_value: Number = -math.inf, max_value: Number = math.inf, **kwargs) -> None:
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if value < self.min_value:
            self.raise_validation_error(path, f'is lower than {self.min_value}')
        if value > self.max_value:
            self.raise_validation_error(path, f'is greater than {self.max_value}')
