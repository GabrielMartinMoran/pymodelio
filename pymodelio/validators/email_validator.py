import re
from typing import Any, Optional

from pymodelio.validators import StringValidator
from pymodelio.validators.validation_patterns import EMAIL_VALIDATION_PATTERN


class EmailValidator(StringValidator):

    def __init__(self, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(nullable=nullable, message=message)

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        # Is override for adding a custom message and validating the string as lowercase
        if re.compile(EMAIL_VALIDATION_PATTERN).match(value.lower()) is None:
            self.raise_validation_error(path, 'is not a valid email address')
