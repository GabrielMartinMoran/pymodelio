# Performing operations after the model was validated via `__once_validated__`
from datetime import datetime
from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    username: Attr(str)

    def __once_validated__(self) -> None:
        self._created_at = datetime.now()

    @property
    def created_at(self) -> datetime:
        return self._created_at


person = Person(username='rick_sanchez')

print(person)
# > Person(created_at=datetime(2023, 4, 24, 10, 33, 16, 780413, None), username='rick_sanchez')
