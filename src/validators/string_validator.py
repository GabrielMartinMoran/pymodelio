import re
import math
from typing import Any

from src.validators.validator import Validator


class StringValidator(Validator):

    def __init__(self, min_len: int = 0, max_len: int = math.inf, fixed_len: int = None, regex: str = None,
                 **kwargs) -> None:
        super().__init__(expected_type=str, **kwargs)
        self.min_len = min_len
        self.max_len = max_len
        self.fixed_len = fixed_len
        self.regex = regex

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if len(value) < self.min_len:
            self.raise_validation_error(path, f'is shorter than {self.min_len}')
        if len(value) > self.max_len:
            self.raise_validation_error(path, f'is longer than {self.max_len}')
        if self.fixed_len is not None and len(value) != self.fixed_len:
            self.raise_validation_error(path, f'length is different than {self.fixed_len}')
        if self.regex is not None and re.compile(self.regex).match(value) is None:
            self.raise_validation_error(path, 'does not match configured regex')
