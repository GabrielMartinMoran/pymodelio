from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    name: Attr(str, default_factory=lambda: 'Unknown')


person = Person()

print(person)
# > Person(name='Unknown')
