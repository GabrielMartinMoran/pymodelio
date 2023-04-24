# Giving an initialization alias to the attribute
from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    __id: Attr(str, init_alias='id')
    _name: Attr(str, init_alias='name')
    occupation: Attr(str, init_alias='person_occupation')

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self._name


person = Person(name='Rick Sánchez', id='0001', person_occupation='Scientist')

print(person)
# > Person(id='0001', name='Rick Sánchez', occupation='Scientist')
