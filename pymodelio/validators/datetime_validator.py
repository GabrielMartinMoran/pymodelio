from datetime import datetime
from typing import Optional

from pymodelio.validators.validator import Validator


class DatetimeValidator(Validator):

    def __init__(self, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=datetime, nullable=nullable, message=message)
