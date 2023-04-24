from datetime import datetime
from typing import Optional
from pymodelio import Attr, PymodelioModel


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
# > Person(age=70, created_at=datetime(2023, 4, 18, 12, 14, 40, 841897, None), grandchild=Person(age=14,
#       created_at=datetime(2023, 4, 18, 12, 14, 40, 841900, None), grandchild=None, name='Morty Smith'),
#       name='Rick Sánchez')
