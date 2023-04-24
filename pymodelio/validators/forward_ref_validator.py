from typing import Any, Optional, ForwardRef

from pymodelio import shared_vars
from pymodelio.validators import Validator


class ForwardRefValidator(Validator):
    __slots__ = Validator.__slots__ + ('_ref',)

    def __init__(self, ref: ForwardRef, nullable: bool = False, message: Optional[str] = None) -> None:
        self._ref = ref
        super().__init__(expected_type=ForwardRef, nullable=nullable, message=message)

    def validate(self, value: Any, path: str = None) -> None:
        if self._expected_types == (ForwardRef,):
            try:
                evaluated = self._ref._evaluate({**globals(), **shared_vars.model_globals}, locals())
                self._expected_types = (evaluated,)
            except NameError:
                print(
                    'Forwarded reference \'%s\' was not loaded at the moment of the validation, skipping validation.'
                    % self._ref.__forward_arg__
                )
                return
        super().validate(value, path)
