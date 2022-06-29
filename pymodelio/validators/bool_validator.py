from typing import Optional

from pymodelio.validators.validator import Validator


class BoolValidator(Validator):

    def __init__(self, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=bool, nullable=nullable, message=message)
