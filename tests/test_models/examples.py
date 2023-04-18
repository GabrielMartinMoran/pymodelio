from datetime import datetime
from typing import Optional

from pymodelio import Attr, PymodelioModel, PymodelioSettings, PymodelioSetting

PymodelioSettings.set(PymodelioSetting.USE_CACHE_OPTIMIZATIONS, False)


# Example 1

class Person(PymodelioModel):
    name: Attr(str)
    created_at: Attr(datetime)
    age: Attr(int)

    def describe(self) -> str:
        return f'{self.name} is {self.age} years old, and it was created on {self.created_at}'


person = Person(name='Rick Sánchez', created_at=datetime.now(), age=70)

print(person)

# > Person(age=70, created_at=datetime(2023, 4, 18, 11, 46, 25, 978204, None), name='Rick Sánchez')

print(person.describe())


# > Rick Sánchez is 70 years old, and it was created on 2023-04-18 13:16:01.838463

# Example 2
class Pet(PymodelioModel):
    name: Attr(str)


class Person(PymodelioModel):
    name: Attr(str)
    created_at: Attr(datetime)
    age: Attr(int)
    pet: Attr(Pet)


person = Person(name='Morty Smith', created_at=datetime.now(), age=14, pet=Pet(name='Snuffles'))

print(person)


# > Person(age=14, created_at=datetime(2023, 4, 18, 12, 13, 0, 852099, None), name='Morty Smith', pet=Pet(name='Snuffles'))


# Example 3
class Person(PymodelioModel):
    name: Attr(str)
    created_at: Attr(datetime)
    age: Attr(int)
    grandchild: Attr(Optional['Person'])


person = Person(
    name='Rick Sánchez', created_at=datetime.now(), age=70,
    grandchild=Person(
        name='Morty Smith', created_at=datetime.now(), age=14
    )
)

print(person)


# > Person(age=70, created_at=datetime(2023, 4, 18, 12, 14, 40, 841897, None), grandchild=Person(age=14, created_at=datetime(2023, 4, 18, 12, 14, 40, 841900, None), grandchild=None, name='Morty Smith'), name='Rick Sánchez')


class CustomModel(PymodelioModel):

    def __before_init__(self, *args, **kwargs) -> None:
        print('__before_init__')

    def __before_validate__(self) -> None:
        print('__before_validate__')

    def __once_validated__(self) -> None:
        print('__once_validated__')


CustomModel()
