import uuid

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    internal_id: Attr(str, initable=False, default_factory=lambda: str(uuid.uuid4()))


person = Person()

print(person)
# > Person(internal_id='c607c97e-4ec1-49e4-83dd-28aa1def7a13')

# Warning! The next line will raise: NameError: internal_id attribute is not initable for class Person
person = Person(internal_id='custom id')
