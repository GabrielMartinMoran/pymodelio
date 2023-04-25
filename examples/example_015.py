# Customizing model comparison
from datetime import datetime
from typing import Optional

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    _id: Attr(str, init_alias='id')
    name: Attr(Optional[str])
    created_at: Attr(datetime, compare=False)


person_1 = Person(id='0001', name='Rick Sanchez', created_at=datetime.now())
person_2 = Person(id='0001', name='Rick Sanchez', created_at=datetime.now())
person_3 = Person(id='0002', name='Morty Smith', created_at=datetime.now())

print(person_1 == person_2)
# > True

print(person_1 == person_3)
# > False
