from src.validators.validator import Validator


class DictValidator(Validator):

    def __init__(self, **kwargs) -> None:
        super().__init__(expected_type=dict, **kwargs)
