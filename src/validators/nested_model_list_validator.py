from typing import Any

from src.validators.validator import Validator


class NestedModelListValidator(Validator):

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if not isinstance(value, list):
            self.raise_validation_error(path, 'is not a valid list')
        for i, x in enumerate(value):
            subpath = f'{path}[{i}]'
            if not hasattr(x, 'validate'):
                raise NotImplementedError(f'{x}[{i}] model does not implement validate method')
            x.validate(subpath)
