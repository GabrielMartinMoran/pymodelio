# Preventing property serialization by using `@do_not_serialize` decorator
from pymodelio import Attr, PymodelioModel, do_not_serialize


class Person(PymodelioModel):
    _name: Attr(str, init_alias='name')

    @property
    def name(self) -> str:
        return self._name

    @property
    @do_not_serialize
    def lowercase_name(self) -> str:
        # This property won't be automatically serialized
        return self._name.lower()


person = Person(name='Rick Sanchez')

serialized = person.to_dict()

print(serialized)
# > {'name': 'Rick Sanchez'}
