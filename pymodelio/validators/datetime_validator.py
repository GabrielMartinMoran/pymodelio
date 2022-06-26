from datetime import datetime

from pymodelio.validators.validator import Validator


class DatetimeValidator(Validator):

    def __init__(self, **kwargs) -> None:
        super().__init__(expected_type=datetime, **kwargs)
