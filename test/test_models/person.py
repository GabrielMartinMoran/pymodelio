import uuid
from typing import List

from src.model import pymodelio_model
from src.attribute import Attribute
from src.validators.string_validator import StringValidator
from src.validators.validator import Validator


@pymodelio_model
class PersonNestedModel:
    id: Attribute[str](default_factory=lambda: uuid.uuid4().__str__())


@pymodelio_model
class Person:
    _dni: Attribute[str](validator=StringValidator(fixed_len=8))
    _name: Attribute[str](validator=StringValidator())
    __private_default_attr: Attribute[str](default_factory=lambda: 'Hi from private default!')
    public_attr: Attribute[str]
    nested_model: Attribute[PersonNestedModel](Validator())
    nested_models: Attribute[List[PersonNestedModel]](default_factory=lambda: [])

    def __before_init__(self, *args, **kwargs) -> None:
        self._instance_attr = kwargs.get('instance_attr')

    @classmethod
    def __once_validated__(cls) -> None:
        print('Hi from Person __once_validated__')

    @property
    def dni(self) -> int:
        return self._dni

    @property
    def name(self) -> str:
        return self._name

    @property
    def private_default_attr(self) -> str:
        return self.__private_default_attr
