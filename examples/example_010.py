# Customizing the deserialization process with `@deserializes`
from pymodelio import Attr, PymodelioModel
from pymodelio.decorators.deserializes import deserializes


class Person(PymodelioModel):
    __id: Attr(str, init_alias='id')
    _name: Attr(str, init_alias='name')
    occupation: Attr(str, init_alias='person_occupation')
    age: Attr(int)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self._name

    @deserializes('id')
    def _deserialize_id(self, value: str) -> str:
        return str(int(value))

    @deserializes(['name', 'person_occupation'])
    def _deserialize_name_and_person_occupation(self, value: str) -> str:
        return value.title()

    @deserializes('age')
    def _deserialize_age(self, value: str) -> int:
        return int(value)


person = Person.from_dict({'name': 'rick sánchez', 'id': '0001', 'person_occupation': 'SCIENTIST', 'age': '70'})

print(person)
# > Person(age=70, id='1', name='Rick Sánchez', occupation='Scientist')
