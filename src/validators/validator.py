from typing import Any

from src.exceptions.model_validation_exception import ModelValidationException


class Validator:

    def __init__(self, nullable: bool = False, message: str = None) -> None:
        self.nullable = nullable
        self.message = message

    def validate(self, value: Any, path: str = None) -> None:
        if value is None and not self.nullable:
            self.raise_validation_error(path, 'must not be None')

    def raise_validation_error(self, path: str, message: str) -> None:
        _message = message if self.message is None else self.message
        raise ModelValidationException(f'{path} {_message}')
