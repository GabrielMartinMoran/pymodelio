import re
from datetime import datetime
from typing import List

from pymodelio import PymodelioModel
from pymodelio.attribute import Attr
from pymodelio.validators.int_validator import IntValidator
from pymodelio.validators.string_validator import StringValidator


class PymodelioChildModel(PymodelioModel):
    public_child_attr: Attr(int)


class PymodelioParentModel(PymodelioModel):
    public_attr: Attr(int, validator=IntValidator(min_value=0, max_value=10))
    _protected_attr: Attr(str, validator=StringValidator(fixed_len=5, regex='^[A-Z]+$'))  # Only capitalized chars
    __private_attr: Attr(datetime)
    child_model_attr: Attr(PymodelioChildModel)
    children_model_attr: Attr(List[PymodelioChildModel])
    optional_attr: Attr(dict, default_factory=dict)
    non_initable_attr: Attr(List[str], initable=False, default_factory=list)


class RawPythonChildModel:

    def __int__(self, public_child_attr: int) -> None:
        self.public_child_attr = public_child_attr
        self.validate()

    def validate(self) -> None:
        assert isinstance(self.public_child_attr, int), 'public_child_attr is not instance of int'


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
        assert isinstance(self.public_attr, int), 'public_child_attr is not instance of int'
        assert self.public_attr >= self._PUBLIC_ATTR_MIN_VALUE, \
            f'public_child_attr is less than {self._PUBLIC_ATTR_MIN_VALUE}'
        assert self.public_attr <= self._PUBLIC_ATTR_MAX_VALUE, \
            f'public_child_attr is greater than {self._PUBLIC_ATTR_MAX_VALUE}'

        assert isinstance(self._protected_attr, str), '_protected_attr is not instance of str'
        assert len(self._protected_attr) == self._PROTECTED_ATTR_FIXED_LENGTH, \
            f'_protected_attr length is different than {self._PROTECTED_ATTR_FIXED_LENGTH}'
        assert re.compile(self._PROTECTED_ATTR_REGEX).match(self._protected_attr) is not None, \
            '_protected_attr does not match configured regex'

        assert isinstance(self.child_model_attr, RawPythonChildModel), \
            'child_model_attr is not instance of RawPythonChildModel'
        self.child_model_attr.validate()

        assert isinstance(self.children_model_attr, list), 'children_model_attr is not instance of list'
        for child_model in self.children_model_attr:
            child_model.validate()

        assert isinstance(self.__private_attr, datetime), '__private_attr is not instance of datetime'

        assert isinstance(self.optional_attr, dict), 'optional_attr is not instance of dict'
