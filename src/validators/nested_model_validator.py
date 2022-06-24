from typing import Any

from src.validators.validator import Validator


class NestedModelValidator(Validator):

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if not hasattr(value, 'validate'):
            NotImplementedError(f'{value} model does not implement validate method')
        value.validate(path)
