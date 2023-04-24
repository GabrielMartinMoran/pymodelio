from typing import Optional

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    name: Attr(Optional[str])


person = Person()

print(person)
# > Person(name=None)
