from typing import Any, Union, List, Optional

from pymodelio.validators.validator import Validator


class ListValidator(Validator):

    def __init__(self, elements_type: Union[type, List[type]], nullable: bool = False,
                 message: Optional[str] = None) -> None:
        super().__init__(expected_type=list, nullable=nullable, message=message)
        self.elements_type = tuple(elements_type) if isinstance(elements_type, (list, tuple, set)) else (elements_type,)

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        for i, x in enumerate(value):
            sub_path = f'{path}[{i}]'

            if not isinstance(x, self.elements_type):
                self.raise_validation_error(sub_path,
                                            f'is not a valid {" or ".join([t.__name__ for t in self.elements_type])}')
            # If it is a model
            if hasattr(x, 'validate'):
                x.validate(sub_path)
