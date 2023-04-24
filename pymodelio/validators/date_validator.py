from datetime import date
from typing import Optional

from pymodelio.validators.validator import Validator


class DateValidator(Validator):

    def __init__(self, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=date, nullable=nullable, message=message)
