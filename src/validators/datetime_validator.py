from datetime import datetime
from typing import Any

from src.validators.validator import Validator


class DatetimeValidator(Validator):

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if not isinstance(value, datetime):
            self.raise_validation_error(path, 'is not a valid datetime')
