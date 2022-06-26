from typing import Any, Union, List, Optional

from pymodelio.exceptions.model_validation_exception import ModelValidationException


class Validator:

    def __init__(self, expected_type: Union[type, List[type]] = None, nullable: bool = False,
                 message: Optional[str] = None) -> None:
        self.nullable = nullable
        self.message = message
        if expected_type is None:
            self._expected_types = None
        else:
            self._expected_types = tuple(expected_type) if isinstance(expected_type, (list, tuple, set)) else (
                expected_type,)

    def validate(self, value: Any, path: str = None) -> None:
        if value is None:
            if not self.nullable:
                self.raise_validation_error(path, 'must not be None')
            return
        if self._expected_types is not None and not isinstance(value, self._expected_types):
            self.raise_validation_error(path,
                                        f'is not a valid {" or ".join([t.__name__ for t in self._expected_types])}')
        # If it is a model
        if hasattr(value, 'validate'):
            value.validate(path)

    def raise_validation_error(self, path: str, message: str) -> None:
        _message = message if self.message is None else self.message
        raise ModelValidationException(f'{path} {_message}')
