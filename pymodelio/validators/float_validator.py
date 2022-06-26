from typing import Optional

from pymodelio.validators.numeric_validator import NumericValidator


class FloatValidator(NumericValidator):

    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, nullable: bool = False,
                 message: Optional[str] = None) -> None:
        super().__init__(expected_type=float, min_value=min_value, max_value=max_value, nullable=nullable,
                         message=message)
