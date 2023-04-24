from datetime import datetime
from pymodelio import Attr, PymodelioModel


class Pet(PymodelioModel):
    name: Attr(str)


class Person(PymodelioModel):
    name: Attr(str)
    created_at: Attr(datetime)
    age: Attr(int)
    pet: Attr(Pet)


person = Person(name='Morty Smith', created_at=datetime.now(), age=14, pet=Pet(name='Snuffles'))

print(person)
# > Person(age=14, created_at=datetime(2023, 4, 18, 12, 13, 0, 852099, None), name='Morty Smith',
#       pet=Pet(name='Snuffles'))
