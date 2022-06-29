import re
from datetime import datetime
from typing import List

from pymodelio.attribute import Attribute
from pymodelio.model import pymodelio_model
from pymodelio.validators.datetime_validator import DatetimeValidator
from pymodelio.validators import DictValidator
from pymodelio.validators.int_validator import IntValidator
from pymodelio.validators import IterableValidator
from pymodelio.validators.string_validator import StringValidator
from pymodelio.validators.validator import Validator


@pymodelio_model
class PymodelioChildModel:
    public_child_attr: Attribute[int](validator=IntValidator())


@pymodelio_model
class PymodelioModel:
    public_attr: Attribute[int](validator=IntValidator(min_value=0, max_value=10))
    _protected_attr: Attribute[str](validator=StringValidator(fixed_len=5, regex='^[A-Z]+$'))  # Only capitalized chars
    __private_attr: Attribute[datetime](validator=DatetimeValidator())
    child_model_attr: Attribute[PymodelioChildModel](validator=Validator(expected_type=PymodelioChildModel))
    children_model_attr: Attribute[List[PymodelioChildModel]](
        validator=IterableValidator(elements_type=PymodelioChildModel))
    optional_attr: Attribute[dict](validator=DictValidator())
    non_initable_attr: Attribute[List[str]](initable=False, default_factory=list)


class RawPythonChildModel:

    def __int__(self, public_child_attr: int) -> None:
        self.public_child_attr = public_child_attr
        self.validate()

    def validate(self) -> None:
        assert isinstance(self.public_child_attr, int), 'public_child_attr is not a valid int'


class RawPythonModel:
    _PUBLIC_ATTR_MIN_VALUE = 0
    _PUBLIC_ATTR_MAX_VALUE = 0

    _PROTECTED_ATTR_FIXED_LENGTH = 5
    _PROTECTED_ATTR_REGEX = '^[A-Z]+$'  # Only capitalized chars

    def __init__(self, public_attr: int, protected_attr: str, private_attr: datetime,
                 child_model_attr: RawPythonChildModel, children_model_attr: List[RawPythonChildModel],
                 optional_attr: dict = None) -> None:
        self.public_attr = public_attr
        self._protected_attr = protected_attr
        self.__private_attr = private_attr
        self.child_model_attr = child_model_attr
        self.children_model_attr = children_model_attr
        self.optional_attr = {} if optional_attr is None else optional_attr
        self.non_initable_attr = []
        self.validate()

    def validate(self) -> None:
        assert isinstance(self.public_attr, int), 'public_child_attr is not a valid int'
        assert self.public_attr >= self._PUBLIC_ATTR_MIN_VALUE, \
            f'public_child_attr is lower than {self._PUBLIC_ATTR_MIN_VALUE}'
        assert self.public_attr <= self._PUBLIC_ATTR_MAX_VALUE, \
            f'public_child_attr is greater than {self._PUBLIC_ATTR_MAX_VALUE}'

        assert isinstance(self._protected_attr, str), '_protected_attr is not a valid str'
        assert len(self._protected_attr) == self._PROTECTED_ATTR_FIXED_LENGTH, \
            f'_protected_attr length is different than {self._PROTECTED_ATTR_FIXED_LENGTH}'
        assert re.compile(self._PROTECTED_ATTR_REGEX).match(self._protected_attr) is not None, \
            '_protected_attr does not match configured regex'

        assert isinstance(self.child_model_attr, RawPythonChildModel), \
            'child_model_attr is not a valid RawPythonChildModel'
        self.child_model_attr.validate()

        assert isinstance(self.children_model_attr, list), 'children_model_attr is not a valid list'
        for child_model in self.children_model_attr:
            child_model.validate()

        assert isinstance(self.__private_attr, datetime), '__private_attr is not a valid datetime'

        assert isinstance(self.optional_attr, dict), 'optional_attr is not a valid dict'
