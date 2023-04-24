# Customizing the initialization workflow using `__before_init__`
import hashlib
from typing import Optional, Any, Dict, Tuple

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    username: Attr(str)
    password: Attr(Optional[str])
    hashed_password: Attr(str)

    def __before_init__(self, *args, **kwargs) -> Tuple[Tuple[Any], Dict[Any, Any]]:
        if 'password' in kwargs and 'hashed_password' not in kwargs:
            _kwargs = {**kwargs, **{'hashed_password': self._hash_password(kwargs['password'])}}
        else:
            _kwargs = kwargs
        return args, _kwargs

    @classmethod
    def _hash_password(cls, pwd: str) -> str:
        return hashlib.md5(pwd.encode('utf-8')).hexdigest()


person = Person(username='rick_sanchez', password='SuperSecurePassword1234')

print(person)
# > Person(hashed_password='e412916d8d95fa958f7552ca30c5bda8', password='SuperSecurePassword1234',
#       username='rick_sanchez')
