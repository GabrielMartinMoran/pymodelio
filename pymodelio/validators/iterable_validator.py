from typing import Any, Union, List, Optional

from pymodelio.validators.validator import Validator


class IterableValidator(Validator):

    def __init__(self, expected_type: Union[type, List[type]] = None, elements_type: Union[type, List[type]] = None,
                 allow_empty: bool = True, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=expected_type, nullable=nullable, message=message)
        self.elements_type = tuple(elements_type) if isinstance(elements_type, (list, tuple, set)) else (elements_type,)
        self.allow_empty = allow_empty

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if len(value) == 0 and not self.allow_empty:
            self._raise_validation_error(path, 'must not be empty')
        for i, x in enumerate(value):
            if self.elements_type != (None,) and not isinstance(x, self.elements_type):
                sub_path = '%s[%s]' % (path, i)
                self._raise_validation_error(
                    sub_path, 'is not instance of %s' % (' or '.join([t.__name__ for t in self.elements_type]))
                )
            # If it is a model
            if hasattr(x, 'validate'):
                sub_path = '%s[%s]' % (path, i)
                x.validate(sub_path)
