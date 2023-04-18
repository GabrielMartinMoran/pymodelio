import re
from typing import Any, Optional

from pymodelio.validators.validator import Validator


class StringValidator(Validator):

    def __init__(self, min_len: Optional[int] = None, max_len: Optional[int] = None, fixed_len: Optional[int] = None,
                 regex: Optional[str] = None, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=str, nullable=nullable, message=message)
        self.min_len = min_len
        self.max_len = max_len
        self.fixed_len = fixed_len
        self.regex = regex

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if self.min_len is not None and len(value) < self.min_len:
            self.raise_validation_error(path, 'is shorter than %s' % self.min_len)
        if self.max_len is not None and len(value) > self.max_len:
            self.raise_validation_error(path, 'is longer than %s' % self.max_len)
        if self.fixed_len is not None and len(value) != self.fixed_len:
            self.raise_validation_error(path, 'length is different than %s' % self.fixed_len)
        if self.regex is not None and re.compile(self.regex).match(value) is None:
            self.raise_validation_error(path, 'does not match configured regex')
