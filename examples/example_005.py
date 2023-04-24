# Giving multiple initialization aliases to the attribute
from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    __id: Attr(str, init_aliases=['id', '$id'])
    _name: Attr(str, init_aliases=['name', '_name'])
    occupation: Attr(str, init_aliases=['occupation', '_occupation'])

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self._name


person = Person(name='Rick Sánchez', id='0001', occupation='Scientist')

print(person)
# > Person(id='0001', name='Rick Sánchez', occupation='Scientist')

person = Person.from_dict({'_name': 'Morty Smith', '$id': '0002', '_occupation': 'Student'})

print(person)
# > Person(id='0002', name='Morty Smith', occupation='Student')
