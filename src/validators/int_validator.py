from src.validators.numeric_validator import NumericValidator


class IntValidator(NumericValidator):

    def __init__(self, **kwargs) -> None:
        super().__init__(int, **kwargs)
