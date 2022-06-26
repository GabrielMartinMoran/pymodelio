from pymodelio.validators.numeric_validator import NumericValidator


class FloatValidator(NumericValidator):

    def __init__(self, **kwargs) -> None:
        super().__init__(expected_type=float, **kwargs)
