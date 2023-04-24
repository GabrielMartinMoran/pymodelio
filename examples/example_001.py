from datetime import datetime
from pymodelio import Attr, PymodelioModel


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
