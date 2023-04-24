# Customizing the initialization workflow using `__before_validate__`
import hashlib
from typing import Optional

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    username: Attr(str)
    password: Attr(Optional[str])
    hashed_password: Attr(str)

    def __before_validate__(self) -> None:
        if self.hashed_password is None and self.password is not None:
            self.hashed_password = self._hash_password(self.password)

    @classmethod
    def _hash_password(cls, pwd: str) -> str:
        return hashlib.md5(pwd.encode('utf-8')).hexdigest()


person = Person(username='rick_sanchez', password='SuperSecurePassword1234')

print(person)
# > Person(hashed_password='e412916d8d95fa958f7552ca30c5bda8', password='SuperSecurePassword1234',
#       username='rick_sanchez')
