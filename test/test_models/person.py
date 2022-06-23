import uuid
from typing import List

from src.base_model import BaseModel
from src.validated import Validated


class PersonNestedModel(BaseModel):
    id: Validated[str](default_factory=lambda: uuid.uuid4().__str__(), auto_validate=False)


class Person(BaseModel):
    _dni: Validated[int](nullable=False)
    _name: Validated[str](nullable=False)
    __private_default_attr: Validated[str](default_factory=lambda: 'Hi from private default!')
    public_attr: Validated[str]
    nested_model: Validated[PersonNestedModel](nullable=False)
    nested_models: Validated[List[PersonNestedModel]](nullable=False, default_factory=lambda: [])

    @property
    def dni(self) -> int:
        return self._dni

    @property
    def name(self) -> str:
        return self._name

    @property
    def private_default_attr(self) -> str:
        return self.__private_default_attr
