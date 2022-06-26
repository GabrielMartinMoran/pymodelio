from typing import Optional

from pymodelio.validators.numeric_validator import NumericValidator


class IntValidator(NumericValidator):

    def __init__(self, min_value: Optional[int] = None, max_value: Optional[int] = None, nullable: bool = False,
                 message: Optional[str] = None) -> None:
        super().__init__(expected_type=int, min_value=min_value, max_value=max_value, nullable=nullable,
                         message=message)
