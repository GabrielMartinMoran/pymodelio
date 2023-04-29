[![Python v3.8+](https://img.shields.io/badge/Python-v3.8%2B-blue)](https://www.python.org/downloads)
[![Python tests](https://github.com/GabrielMartinMoran/pymodelio/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/GabrielMartinMoran/pymodelio/actions/workflows/python.yml)
[![codecov](https://codecov.io/gh/GabrielMartinMoran/pymodelio/branch/main/graph/badge.svg?token=VVKW3GDMLD)](https://codecov.io/gh/GabrielMartinMoran/pymodelio)

# [pymodelio](https://github.com/GabrielMartinMoran/pymodelio)

A simple Python module for defining rich domain models, serializing, deserializing and validating them.

# What is this module for?

Have you ever needed to validate a user input, the body of a request, data obtained from a service like a database or
an external api, without needing to also define serializers and deserializers for your class nested data structure?
Well, that's what `pymodelio` is built for, simplicity when defining your domain models and the surrounding
restrictions.

# Installation

Installing the module is simple as running the following script on your terminal.

```shell
pip install -U pymodelio
```

# How can I use this module?

## Table of contents

- [Declaring models](#declaring-models)
- [Comparing models](#comparing-models)
- [Attribute's validation](#attributes-validation)
- [Serialization and deserialization](#serialization-and-deserialization)
- [Configuring pymodelio settings](#configuring-pymodelio-settings)
- [Comparing pymodelio with other options](#comparing-pymodelio-with-other-options)

## Declaring models

Pymodelio models are declared by inheriting from `PymodelioModel` class. When instantiating a model, all _initable_
declared attributes should be provided (if not, default generated from _default_factory_ builders will be used instead).

### Let's begin with a simple example

**Example 1 - Creating our first pymodelio's model**

```py
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
```

_IMPORTANT NOTE:_ Note that pymodelio attributes are defined by using Python type annotations, so we are not setting dafault values to static class attributes. Also, when you interact with these attibutes, the code autocompletion engine is going to autocomplete with the methods and properties of attribute type you specified as the first parameter of `Attr` (because on runtime you will be really working with that attribute type). For instance when interacting with `name` inside of the class, that prop will we considered as a `str`.

### What about using models from other models?

**Example 2 - Using nested models**

```py
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
```

### What about using a model within the same model?

For doing this, we need to use [forward references](https://peps.python.org/pep-0484/#forward-references) when using the `Person` model, because it was not yet initialized during the attribute declaration.

**Example 3 - Using the same model as a nested one**

```py
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
```

### How can I itinialize protected or private attributes

Even when Python doesn't implement a strict way of definig _protected_ or _private_ attributes, there is a commonly used convention that says: Adding a single underscore as a prefix of the attribute name (like `_name`) suggests that that attribute is _protected_. Also, adding a double underscore as a prefix of the attribute name (like `__id`), suggests that that attribute is _private_.

Pymodelio provides multiple ways of letting you initialize _protected_ and _private_ attributes either from the class constructor or from the deserializer factory constructor (expained later in this documentation). These ways of doing this are:

- **Giving an initialization alias to the attribute:** Passing the `init_alias` parameter to the `Attr` function, you can define an alias used to map values from in the constructors.
- **Giving multiple initialization aliases to the attribute:** Passing the `init_aliases` parameter to the `Attr` function, you can define multiple aliases used to map values from in the constructors.

It's important to know that these aliases are only for populating the model from the constructors. So all the interactions within the model with the attributes defined like these and from other models are done using the _real_ name of the attribute, not the aliased one.

Let's see some examples of this:

**Example 4 - Giving an initialization alias to an attribute**

```py
from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    __id: Attr(str, init_alias='id')
    _name: Attr(str, init_alias='name')
    occupation: Attr(str, init_alias='person_occupation')

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self._name


person = Person(name='Rick Sánchez', id='0001', person_occupation='Scientist')

print(person)
# > Person(id='0001', name='Rick Sánchez', occupation='Scientist')
```

**Example 5 - Giving multiple initialization aliases to an attribute**

```py
from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    __id: Attr(str, init_aliases=['id', '$id'])
    _name: Attr(str, init_aliases=['name', '_name'])
    occupation: Attr(str, init_aliases=['occupation', '_occupation'])

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self._name


person = Person(name='Rick Sánchez', id='0001', occupation='Scientist')

print(person)
# > Person(id='0001', name='Rick Sánchez', occupation='Scientist')

person = Person.from_dict({'_name': 'Morty Smith', '$id': '0002', '_occupation': 'Student'})

print(person)
# > Person(id='0002', name='Morty Smith', occupation='Student')
```

In this example, we can also see other resource that pymodelio provides. The `from_dict` factory constructor we mentioned befor. Instead of initializing a models using their constructors, we can deserialize them from python dictionaries by calling the `from_dict` method of any pymodelio model.

### Now we are ready too see a more complex example

In this example we will use the concepts we learned before and also customize some of the validators. Because yes, when you don't pass the `validator` parameter to the `Attr` function, it assumes the vaidator based on the type you provided as the first parameter of the function.

But caution, only these types can be automatically inferred by pymodelio:

- `PymodelioModels` _[*]_
- `non-pymodelio classes` _[*]_ (it only validates nullability and performs instance check)
- `str` _[*]_
- `bool` _[*]_
- `int` _[*]_
- `float` _[*]_
- `dict` _[*]_
- `list` _[*]_
- `set` _[*]_
- `tuple` _[*]_
- `date` (from `datetime.date`) _[*]_
- `datetime` (from `datetime.datetime`) _[*]_
- `typing.Dict` (Dict[_x_] where _x_ is any of the previous types marked as _[*]_)
- `typing.List` (List[_x_] where _x_ is any of the previous types marked as _[*]_)
- `typing.Tuple` (Tuple[_x_] where _x_ is any of the previous types marked as _[*]_)
- `typing.Set` (Set[_x_] where _x_ is any of the previous types marked as _[*]_)
- `typing.Optional` (optional version of all listed before)

Ok, so let's continue with the example...

**Example 6 - A more complex example**

```py
import uuid
from typing import List
from pymodelio import Attr, PymodelioModel
from pymodelio.validators import ListValidator, StringValidator
from pymodelio.validators.int_validator import IntValidator
from pymodelio.validators.validator import Validator


class Component(PymodelioModel):
    __serial_no: Attr(
        str,
        validator=StringValidator(fixed_len=36, regex=r'^[a-z0-9-]+$'),
        default_factory=lambda: uuid.uuid4().__str__(),
        init_alias='serial_no'
    )

    @property
    def serial_no(self) -> str:
        return self.__serial_no


class CPU(Component):
    _frequency: Attr(int, validator=IntValidator(min_value=0), init_alias='frequency')
    _cores: Attr(int, validator=IntValidator(min_value=0), init_alias='cores')

    @property
    def frequency(self) -> int:
        return self._frequency

    @property
    def cores(self) -> int:
        return self._cores


class RAM(Component):
    _frequency: Attr(int, validator=IntValidator(min_value=0), init_alias='frequency')
    _size: Attr(int, validator=IntValidator(min_value=0), init_alias='size')

    @property
    def frequency(self) -> int:
        return self._frequency

    @property
    def size(self) -> int:
        return self._size


class Disk(Component):
    _size: Attr(int, validator=IntValidator(min_value=0), init_alias='size')


class Computer(Component):
    _cpu: Attr(CPU, validator=Validator(expected_type=CPU), init_alias='cpu')
    _rams: Attr(List[RAM], validator=ListValidator(elements_type=RAM, allow_empty=False), init_alias='rams')
    _disks: Attr(List[Disk], validator=ListValidator(elements_type=Disk), init_alias='disks')

    @property
    def cpu(self) -> CPU:
        return self._cpu

    @property
    def rams(self) -> List[RAM]:
        return self._rams

    @property
    def disks(self) -> List[Disk]:
        return self._disks


computer = Computer(
    serial_no='123e4567-e89b-12d3-a456-426614174000',
    cpu=CPU(frequency=3500, cores=8),
    rams=[
        RAM(frequency=1600, size=8),
        RAM(frequency=1800, size=16)
    ],
    disks=[
        Disk(size=1024),
        Disk(size=512)
    ]
)

print(computer)
# > Computer(cpu=CPU(cores=8, frequency=3500, serial_no='24da895d-fd5c-4962-bbcc-0b8af63cf230'),
#   disks=[Disk(serial_no='94f14bb4-f7e9-4290-8296-b0a207347b31'),
#   Disk(serial_no='799433cd-17c2-4078-b689-807c7ec98967')],
#   rams=[RAM(frequency=1600, serial_no='b8a2e748-80e1-4d32-b090-3e87f2b6b2da', size=8),
#   RAM(frequency=1800, serial_no='9e86ce6e-ef99-4520-9151-0e71be89aa5d', size=16)],
#   serial_no='123e4567-e89b-12d3-a456-426614174000')
```

### What happens if I don't provide an attribute when initialializing a model?

Well, this depends on how you configured the attribute.

If you didn't specify any special logic for default values, the default `default_factory` method of the attribute will be called, returning a `None` as we can see in this example:

**Example 7 - Initializing an attribute without providing a value**

```py
from typing import Optional

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    name: Attr(Optional[str])


person = Person()

print(person)
# > Person(name=None)
```

In this example, we typed `name` as `Optional[str]` for not getting a validation error during the insantiation.

But if we pass a custom `default_factory` parameter to the attribute that retuns a string, we don't need to make it nullable, like this:

**Example 8 - Custom default factory**

```py
from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    name: Attr(str, default_factory=lambda: 'Unknown')


person = Person()

print(person)
# > Person(name='Unknown')
```

### Preventing attribute's initialization

What if we don't want to allow an attribute initialization at all? Well, for that can pass another parameter to the `Attr` function called `initable`. If `initable` is `False`, that attribute can't be initialized neither from the class constructor nor the `from_dict` factory constructor.

But be aware that if you provide any of the parameters `init_alias` or `init_aliases` to the `Attr` function, the value of `initable` will be ignored.

**Example 9 - Non-initable attributes**

```py
import uuid

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    internal_id: Attr(str, initable=False, default_factory=lambda: str(uuid.uuid4()))


person = Person()

print(person)
# > Person(internal_id='c607c97e-4ec1-49e4-83dd-28aa1def7a13')

# Warning! The next line will raise: NameError: internal_id attribute is not initable for class Person
person = Person(internal_id='custom id')
```

### Customizing the deserialization process

When you want to customize the serialization process of an attribute, you can use the `@deserializes` decorator specifying the alias (in case you specified it) to apply a special treatment to. This custom deserialized will _only_ be used when the model is instantiated via the `from_dict` factory constructor, not when initialized by using the class constructor.

`@deserializes` decorator can receive as a parameter, a string or an iterable of string that represent the names or aliases (if defined) to deserialize with the decorated function.

**Example 10 - Customizing the deserialization process with `@deserializes`**

```py
from pymodelio import Attr, PymodelioModel
from pymodelio.decorators.deserializes import deserializes


class Person(PymodelioModel):
    __id: Attr(str, init_alias='id')
    _name: Attr(str, init_alias='name')
    occupation: Attr(str, init_alias='person_occupation')
    age: Attr(int)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self._name

    @deserializes('id')
    def _deserialize_id(self, value: str) -> str:
        return str(int(value))

    @deserializes(['name', 'person_occupation'])
    def _deserialize_name_and_person_occupation(self, value: str) -> str:
        return value.title()

    @deserializes('age')
    def _deserialize_age(self, value: str) -> int:
        return int(value)


person = Person.from_dict({'name': 'rick sánchez', 'id': '0001', 'person_occupation': 'SCIENTIST', 'age': '70'})

print(person)
# > Person(age=70, id='1', name='Rick Sánchez', occupation='Scientist')
```

The method that is decorated by `@deserializes` should have this structure (you can modify the type of the `value` parameter and the output for linting purposes as we did in the example above).

```py
@deserializes('exposed_attribute_name')
def any_method_name(self, value: Any) -> Any:
    processed_value = ... # Any processing you want
    return processed_value
```

### Customizing the model's initialization workflow

There are some dunder methods that can be overridden in any pymodelio's model for adding custom logic to the model's initializatio workflow.

These dunder method are:

```py
class Model(PymodelioModel):

    def __before_init__(self, *args, **kwargs) -> Tuple[Tuple[Any], Dict[Any, Any]]:
        # This method is called before any other method when the model's constructor
        # is called (included from_dict()).
        # It receives the same parameters the constructor gets.
        # This method returns args and kwargs for not forcing updating the
        # function arguments (that depending on the context, it can be a bad
        # practice).
        return args, kwargs

    def __before_validate__(self) -> None:
        # This method is called after initializing the model attributes but just before
        # performing the model validations (it will be executed even when
        # auto_validate = False)
        pass

    def __once_validated__(self) -> None:
        # This method is called just after the model validations (it will be
        # executed even if auto_validate = False)
        pass
```

Now that we know this, let's see some example of how to inject custom data into the model's initialization flow using these dunder method.

In this first example, we are hashing a password only if we received a plain password when the model is initialized.

**Example 11 - Customizing the initialization workflow by using `__before_init__`**

```py
import hashlib
from typing import Optional, Any, Dict, Tuple

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    username: Attr(str)
    password: Attr(Optional[str])
    hashed_password: Attr(str)

    def __before_init__(self, *args, **kwargs) -> Tuple[Tuple[Any], Dict[Any, Any]]:
        # This method is called before any other method when the model's constructor
        # is called (included from_dict()).
        # It receives the same parameters the constructor gets.
        # This method returns args and kwargs for not forcing updating the
        # function arguments (that depending on the context, it can be a bad
        # practice).
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
```

How can we solve the same problem, but now using `__before_validate__`?

**Example 12 - Customizing the initialization workflow by using `__before_validate__`**

```py
import hashlib
from typing import Optional

from pymodelio import Attr, PymodelioModel


class Person(PymodelioModel):
    username: Attr(str)
    password: Attr(Optional[str])
    hashed_password: Attr(str)

    def __before_validate__(self) -> None:
        # This method is called after initializing the model attributes but just before
        # performing the model validations (it will be executed even when
        # auto_validate = False)
        if self.hashed_password is None and self.password is not None:
            self.hashed_password = self._hash_password(self.password)

    @classmethod
    def _hash_password(cls, pwd: str) -> str:
        return hashlib.md5(pwd.encode('utf-8')).hexdigest()


person = Person(username='rick_sanchez', password='SuperSecurePassword1234')

print(person)
# > Person(hashed_password='e412916d8d95fa958f7552ca30c5bda8', password='SuperSecurePassword1234',
#       username='rick_sanchez')
```

When you need to perform some model logic once the validation process has ended, you can override the `__once_validated__` method.

It's possible to use `__once_validated__` for implementing some custom validations if you need so, but for that specific case it would be a better practice to implement your custom validator by inheriting from pymodelio validator (then we will go deeper into this topic).

**Example 13 - Performing operations after the model was validated via `__once_validated__`**

```py
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
```

In the example above, we can see that we injected a non-pymodelio attribute into the model by using the `__once_validated__` method. This is possible, but it's _important_ to know that non pymodelio attributes will be serialized or included in the string representation of the model **only** if they are exposed by using the `@property` decorator.

This example helped for showing one possible usage of the `__once_validated__` method, but for this specific case, it would be a better practice to define `_created_at` as a non-intable attribute with a custom `default_factory` function that initializes it.

### Attribute's validation

One principle which this module is stood on, is that an instance of a domain model shouldn't exist if it is not
valid. For ensuring that, pymodelio automatically validates the instantiated models if you don't specify the opposite
by passing the parameter `auto_validate=False` for either the class constructor or the `from_dict` factory constructor.

So, it's important have in mind that for performance improvements, we could disable auto validation in nested models initialization when using the constructor way of instantiating our models because when the parent validator is called, it will validate the whole structure.

**Example 14 - Disabling auto validate in children for improving performance**

```py
from typing import List

from pymodelio import Attr, PymodelioModel


class ChildModel(PymodelioModel):
    attr: Attr(str)


class ParentModel(PymodelioModel):
    children: Attr(List[ChildModel])


parent_model = ParentModel(
    children=[
        ChildModel(attr='child_1', auto_validate=False),
        ChildModel(attr='child_2', auto_validate=False),
        ChildModel(attr='child_3', auto_validate=False)
    ]
)

print(parent_model)
# > ParentModel(children=[ChildModel(attr='child_1'), ChildModel(attr='child_2'), ChildModel(attr='child_3')])
```

### Reserved attribute names

Some dunder attributes are used by pymodelio in its models, there attributes shouldn't be declared in the defined models because they will be overridden when loading the class.

These reserved attribute names are:

- `__is_pymodelio_model__`
- `__inner_pymodelio_model__`
- `__is_pymodelio_inner_model__`
- `__model_attrs__`
- `__pymodelio_parent__`
- `__serializable_attrs__`
- `__exposed_attrs__`
- `__protected_attrs__`
- `__private_attrs__`
- `__deserializers__`

## Comparing models

Pymodelio models implement comparison for checking if a model has the same attribute values as other models. By default, all attributes are marked for comparison, but you can customize that by specifying the `compare` parameter of the `Attr` function.

**Example 15 - Customizing model comparison**

```py
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
```

In the example above, we are ignoring `created_at` when comparing models, that's why `person_1` is the equals to `person_2`.

## Attribute's validation

In terms of validators, pymodelio provides already implementing validators that simplifies a lot of use cases, like validating an email, the
length of a string, the range of a number, the emptiness of a list, etc.

### Available validators

**Validator**

A generic validator for any type passed by parameter. It is also capable of validating other models. Validated value
must implement `validate` method in order to be considered a model by this validator.
Other validators inherit from this one.

```py
Validator(expected_type: Union[type, List[type]] = None, nullable: bool = False, message: Optional[str] = None)
```

**StringValidator**

```py
StringValidator(min_len: Optional[int] = None, max_len: Optional[int] = None, fixed_len: Optional[int] = None, regex:
Optional[str] = None, nullable: bool = False, message: Optional[str] = None)
```

**NumericValidator**

```py
NumericValidator(expected_type: type, min_value: Optional[Number] = None, max_value: Optional[
    Number] = None, expected_type: Union[type, List[type]] = None, nullable: bool = False, message: Optional[
    str] = None)
```

**IntValidator**

A subclass of NumericValidator specific for integers.

```py
IntValidator(min_value: Optional[int] = None, max_value: Optional[int] = None, nullable: bool = False, message:
Optional[str] = None)
```

**FloatValidator**

A subclass of NumericValidator specific for float numbers.

```py
FloatValidator(min_value: Optional[float] = None, max_value: Optional[float] = None, nullable: bool = False, message:
Optional[str] = None)
```

**DateValidator**

```py
DateValidator(nullable: bool = False, message: Optional[str] = None)
```

**DatetimeValidator**

```py
DatetimeValidator(nullable: bool = False, message: Optional[str] = None)
```

**DictValidator**

```py
DictValidator(nullable: bool = False, message: Optional[str] = None)
```

**IterableValidator**

A validator for an of any type that allows nested models. Validated children must implement `validate` method in
order to be considered a model by this validator.

```py
IterableValidator(expected_type: Union[type, List[type]] = None, elements_type: Union[
    type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message: Optional[str] = None)
```

**ListValidator**

A subclass of IterableValidator specific for lists.

```py
ListValidator(elements_type: Union[type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message:
Optional[str] = None)
```

**SetValidator**

A subclass of IterableValidator specific for sets.

```py
SetValidator(elements_type: Union[type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message:
Optional[str] = None)
```

**TupleValidator**

A subclass of IterableValidator specific for tuples.

```py
TupleValidator(elements_type: Union[type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message:
Optional[str] = None)
```

**EmailValidator**

```py
EmailValidator(nullable: bool = False, message: Optional[str] = None)
```

**BoolValidator**

```py
BoolValidator(nullable: bool = False, message: Optional[str] = None)
```

**ForwardRefValidator**

A validator used for forwarded references (see `typing.ForwardRef` for more info in `typing` module documentation). The expected type of the validator is intended to be always a _PymodelioModel_ and it's obtained when validating the attribute the first time.

```py
ForwardRefValidator(ref: ForwardRef, nullable: bool = False, message: Optional[str] = None)
```

### Customizing the validation process

Even if a validator is not already implemented,
you can do it in a very siple way by inheriting from `Validator` class or using some exposed middleware model initialization methods.

**Example 16 - Creating a custom validator and using it**

```py
from typing import List, Optional, Any

from pymodelio import Attr, PymodelioModel
from pymodelio.exceptions import ModelValidationException
from pymodelio.validators import Validator


class SpecificStringValidator(Validator):

    def __init__(self, possible_values: List[Any], nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=str, nullable=nullable, message=message)
        self._possible_values = possible_values

    def validate(self, value: Any, path: str = None) -> None:
        super().validate(value, path)
        if value is None:
            return
        if value not in self._possible_values:
            self._raise_validation_error(path, f'must be one of {self._possible_values}')


class CustomModel(PymodelioModel):
    attr: Attr(str, validator=SpecificStringValidator(possible_values=['A', 'B', 'C']))


try:
    instance = CustomModel(attr='D')
except ModelValidationException as e:
    print(e)
    # > CustomModel.attr must be one of ['A', 'B', 'C']
```

Another way of validating a model if you don't want to implement a custom validator, is to override the dunded method `__when_validating_an_attr__` in the defined model.

`__when_validating_an_attr__` is called right after an attribute validator is or would be called. This method is executed regardless if the attribute has or not a validator (for this you need to provide `validator` parameter as `None`).

**Example 17 - Customizing validation process by implementing `__when_validating_an_attr__`**

```py
from typing import Any

from pymodelio import Attr, PymodelioModel
from pymodelio.attribute import PymodelioAttr
from pymodelio.exceptions import ModelValidationException


class CustomModel(PymodelioModel):
    name: Attr(str)  # As we haven't specified a validator, a StringValidator is inferred
    age: Attr(str, validator=None)

    def __when_validating_an_attr__(self, attr_name: str, attr_value: Any, attr_path: str,
                                    parent_path: str, attr: PymodelioAttr) -> None:
        # As this is called after name validator is called, we know that name is a string
        if attr_name == 'name' and len(attr_value) == 0:
            raise ModelValidationException(f'{attr_path} must not be blank')
        if attr_name == 'age' and attr_value < 0:
            raise ModelValidationException(f'{attr_path} must not be less than zero')


try:
    instance = CustomModel(name='', age=70)
except ModelValidationException as e:
    print(e)
    # > CustomModel.name must not be blank

try:
    instance = CustomModel(name='Rick Sanchez', age=-1)
except ModelValidationException as e:
    print(e)
    # > CustomModel.age must not be less than zero
```

### Force model validations

Pymodelio doesn't validate an attribute each time it is updated, because we don't think that's required in most cases. Instead of this, all pymodelio model have a method called `validate`. You can call this method any time you want to validate your model.

## Serialization and deserialization

We have mentioned someting about serialization and deserialization across this document, but let's see in depth how it works.

### Deserialization

As we mentioned before, pymodelio models have a `from_dict` factory constructor, that is intended to be using for transforming Python dictionaries into model instances.

But you can override this method for customizing the de-serialization process of your models.

**Example 18 - Implementing a custom model's deserializer**

```py
from pymodelio import Attr, PymodelioModel


class CustomModel(PymodelioModel):
    attr: Attr(float)

    @classmethod
    def from_dict(cls, data: dict, auto_validate: bool = True) -> 'CustomModel':
        _attr = data.get('attr', 0.0)
        try:
            _attr = float(_attr)
        except ValueError:
            _attr = 0.0
        return CustomModel(attr=_attr, auto_validate=auto_validate)


instance = CustomModel.from_dict({'attr': '1'})
print(instance)
# > CustomModel(attr=1.0)

instance = CustomModel.from_dict({'attr': 1})
print(instance)
# > CustomModel(attr=1.0)

instance = CustomModel.from_dict({'attr': 'INVALID_FLOAT_VALUE'})
print(instance)
# > CustomModel(attr=0.0)

instance = CustomModel.from_dict({})
print(instance)
# > CustomModel(attr=0.0)
```

### Serialization

For serialization, pymodelio models implement a `to_dict()` method that serializes the public attributes (based on the underscore attribute name's convention mentioned at the beginning of the document) and
properties (defined using the `@property` decorator) into a Python dictionary.

In case of properties (defined using the `@property` decorator) that you don't want to serialize, you can use the
`@do_not_serialize` decorator.

**Example 19 - Preventing property serialization by using `@do_not_serialize` decorator**

```py
from pymodelio import Attr, PymodelioModel, do_not_serialize


class Person(PymodelioModel):
    _name: Attr(str, init_alias='name')

    @property
    def name(self) -> str:
        return self._name

    @property
    @do_not_serialize
    def lowercase_name(self) -> str:
        # This property won't be automatically serialized
        return self._name.lower()


person = Person(name='Rick Sanchez')

serialized = person.to_dict()

print(serialized)
# > {'name': 'Rick Sanchez'}
```

If you want to customize the serialization process of your models, you can override the `to_dict` method.

**Example 20 - Implementing a custom model serializer**

```py
from pymodelio import Attr, PymodelioModel


class CustomModel(PymodelioModel):
    attr: Attr(float)

    def to_dict(self) -> dict:
        return {
            'attr': str(self.attr)
        }


instance = CustomModel(attr=1.0)

serialized = instance.to_dict()

print(serialized)
# {'attr': '1.0'}
```

## Configuring pymodelio settings

As we mentioned before, there are some settings that can be configured by calling the `PymodelioSettings` class. These settigs and their expected types are:

- **PymodelioSetting.AUTO_PARSE_DATES_AS_UTC** (`bool`): If `True`, deserialized date and datetime timezones will be replaced by `UTC`.
- **PymodelioSetting.USE_DEFAULT_ATTR_VALIDATOR_IF_NOT_DEFINED** (`bool`): If a validator is not provided when defining a model attribute (like `Attr(str)`) an automatically inferred validator will be used instead. If disabled, the attribute won't have any validator at all unless you manually specified one.

Updating a setting it's as simple as doing:

```py
PymodelioSettings.set(PymodelioSetting.<setting_name>, <value>)
```

For getting the value of a setting, you can call:

```py
PymodelioSettings.get(PymodelioSetting.<setting_name>)
```

Settings can also be resseted by calling:

```py
PymodelioSettings.reset()
```

## Comparing pymodelio with other options

### Let's compare the same code using raw python against using pymodelio

For this comparison, we are not implementing serialization and de-serialization in the raw Python models (pymodelio
handles this automatically for its models).

**Using raw python**

```py
class RawPythonChildModel:

    def __int__(self, public_child_attr: int) -> None:
        self.public_child_attr = public_child_attr
        self.validate()

    def validate(self) -> None:
        assert isinstance(self.public_child_attr, int), 'public_child_attr is not instance of int'


class RawPythonModel:
    _PUBLIC_ATTR_MIN_VALUE = 0
    _PUBLIC_ATTR_MAX_VALUE = 0

    _PROTECTED_ATTR_FIXED_LENGTH = 5
    _PROTECTED_ATTR_REGEX = '^[A-Z]+$'  # Only capitalized chars

    def __init__(self, public_attr: int, protected_attr: str, private_attr: datetime,
                 child_model_attr: RawPythonChildModel, children_model_attr: List[RawPythonChildModel],
                 optional_attr: dict = None) -> None:
        self.public_attr = public_attr
        self._protected_attr = protected_attr
        self.__private_attr = private_attr
        self.child_model_attr = child_model_attr
        self.children_model_attr = children_model_attr
        self.optional_attr = {} if optional_attr is None else optional_attr
        self.non_initable_attr = []
        self.validate()

    def validate(self) -> None:
        assert isinstance(self.public_attr, int), 'public_child_attr is not instance of int'
        assert self.public_attr >= self._PUBLIC_ATTR_MIN_VALUE,
        f'public_child_attr is lower than {self._PUBLIC_ATTR_MIN_VALUE}'

        assert self.public_attr <= self._PUBLIC_ATTR_MAX_VALUE,
        f'public_child_attr is greater than {self._PUBLIC_ATTR_MAX_VALUE}'

        assert isinstance(self._protected_attr, str), '_protected_attr is not instance of str'
        assert len(self._protected_attr) == self._PROTECTED_ATTR_FIXED_LENGTH,
        f'_protected_attr length is different than {self._PROTECTED_ATTR_FIXED_LENGTH}'
        assert re.compile(self._PROTECTED_ATTR_REGEX).match(self._protected_attr) is not None,
        '_protected_attr does not match configured regex'

        assert isinstance(self.child_model_attr, RawPythonChildModel),
        'child_model_attr is not instance of RawPythonChildModel'
        self.child_model_attr.validate()

        assert isinstance(self.children_model_attr, list), 'children_model_attr is not instance of list'
        for child_model in self.children_model_attr:
            child_model.validate()

        assert isinstance(self.__private_attr, datetime), '__private_attr is not instance of datetime'

        assert isinstance(self.optional_attr, dict), 'optional_attr is not instance of dict'
```

**Using pymodelio**

pymodelio model validation errors also give more information about the full path of nested structures. In case of lists,
including the index of the list element where the error occurred.

```py
class PymodelioChildModel(PymodelioModel):
    public_child_attr: Attr(int)


class PymodelioParentModel(PymodelioModel):
    public_attr: Attr(int, validator=IntValidator(min_value=0, max_value=10))
    _protected_attr: Attr(str, validator=StringValidator(fixed_len=5, regex='^[A-Z]+$'), init_alias='protected_attr')  # Only capitalized chars
    __private_attr: Attr(datetime, init_alias='private_attr')
    child_model_attr: Attr(PymodelioChildModel)
    children_model_attr: Attr(List[PymodelioChildModel])
    optional_attr: Attr(dict, default_factory=dict)
    non_initable_attr: Attr(List[str], initable=False, default_factory=list)

```

### What about comparing attrs, pydantic and pymodelio?

On early releases of this module, most of people wanted like to know why choosing pymodelio over attrs or pydantic. Apart of some unique use cases that pymodelio simplifies a lot (as we described in this documentation), we created a benchmark (that you can run) for comparing these libraries.

For running this benchmark, `attrs`, `pydantic` and `pymodelio` must be installed in your working environment.

In this benchmark, we are comparing:

- The time each library takes for deserializing a model from a dictionary (including the validation run during initialization)
- The time each library takes for serializing a model into a dictionary
- The time each library takes for reading and writting model attributes
- The time each library takes for deserializing a model from invalid data (that results in validation errors)
- Total time of this process

**Give me that benchmark!**

```py
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Callable, Any, Optional
from uuid import uuid4

import attrs
from attrs import asdict, define, field
from pydantic import BaseModel
from pymodelio import Attr, PymodelioModel

NUM_PARENTS = 100
NUM_CHILDREN_PER_PARENT = 1000


# Pydantic models
class PydanticChild(BaseModel):
    identifier: str
    created_at: int
    updated_at: Optional[int]
    data: dict


class PydanticParent(BaseModel):
    identifier: str
    created_at: int
    updated_at: Optional[int]
    children: List[PydanticChild]


# Pymodelio models
class PymodelioChild(PymodelioModel):
    identifier: Attr(str)
    created_at: Attr(int)
    updated_at: Attr(Optional[int])
    data: Attr(dict)


class PymodelioParent(PymodelioModel):
    identifier: Attr(str)
    created_at: Attr(int)
    updated_at: Attr(Optional[int])
    children: Attr(List[PymodelioChild])


# Attrs models
@define
class AttrsChild:
    identifier: str = field(validator=[attrs.validators.instance_of(str)])
    created_at: int = field(validator=[attrs.validators.instance_of(int)])
    data: dict = field(validator=[attrs.validators.instance_of(dict)])
    updated_at: Optional[int] = None


def _validate_children(instance, attribute, value: Any) -> None:
    for x in value:
        assert isinstance(x, AttrsChild), 'Invalid child'


def _convert_to_attrs_children(records):
    return [AttrsChild(**record) for record in records]


@define
class AttrsParent:
    identifier: str = field(validator=[attrs.validators.instance_of(str)])
    created_at: int = field(validator=[attrs.validators.instance_of(int)])
    children: List[AttrsChild] = field(converter=_convert_to_attrs_children,
                                       validator=[attrs.validators.instance_of(list), _validate_children])
    updated_at: Optional[int] = None


@dataclass
class TimeResults:
    name: str
    deserialization: float = 0.0
    serialization: float = 0.0
    valid_data_processing: float = 0.0
    invalid_data_processing: float = 0.0
    attributes_updating: float = 0.0
    total: float = 0.0

    def __repr__(self) -> str:
        return f'Total {self.total} seconds:\n' \
               f'  > Valid data processing (total {self.valid_data_processing} seconds)\n' \
               f'     - Deserialization {self.deserialization} seconds\n' \
               f'     - Serialization {self.serialization} seconds\n' \
               f'  > Attributes updating (total {self.valid_data_processing} seconds)\n' \
               f'  > Invalid data processing (total {self.invalid_data_processing} seconds)\n'


def generate_valid_data() -> List[dict]:
    parents = []
    for x in range(NUM_PARENTS):
        children = []
        for y in range(NUM_CHILDREN_PER_PARENT):
            children.append({
                'identifier': str(uuid4()),
                'created_at': int(datetime.now().timestamp()),
                'data': {
                    f'{random.randint(100, 999)}_sample': random.randint(100_000, 999_999)
                    for x in range(random.randint(1, 5))
                }
            })
        parent = {
            'identifier': str(uuid4()),
            'created_at': int(datetime.now().timestamp()),
            'children': children
        }
        parents.append(parent)
    return parents


def generate_invalid_data() -> List[dict]:
    parents = []
    for x in range(NUM_PARENTS):
        children = []
        for y in range(NUM_CHILDREN_PER_PARENT):
            children.append({
                'identifier': str(uuid4()),
                'created_at': int(datetime.now().timestamp()),
                'data': None
            })
        parent = {
            'identifier': str(uuid4()),
            'created_at': int(datetime.now().timestamp()),
            'children': children
        }
        parents.append(parent)
    return parents


def get_data() -> Tuple[List[dict], List[dict]]:
    print('Creating sample data')
    valid_data = generate_valid_data()
    invalid_data = generate_invalid_data()
    return valid_data, invalid_data


def run_benchmark(name: str, valid_data: List[dict], invalid_data: List[dict],
                  deserialize_function: Callable[[dict], Any],
                  serialize_function: Callable[[Any], Any]) -> TimeResults:
    print(f'\nStarting {name} benchmark...')

    results = TimeResults(name=name)

    start = time.time()

    instances = []

    # Deserialization
    _start = time.time()
    for record in valid_data:
        instances.append(deserialize_function(record))
    results.deserialization = time.time() - _start

    # Serialization
    _start = time.time()
    for instance in instances:
        serialize_function(instance)
    results.serialization = time.time() - _start

    results.valid_data_processing = time.time() - start

    # Updating attributes
    _start = time.time()
    for instance in instances:
        instance.updated_at = int(time.time())
        for child in instance.children:
            child.data = {
                'identifier': child.identifier,
                'created_at': child.created_at
            }
            child.updated_at = int(time.time())
    results.attributes_updating = time.time() - _start

    # Invalid processing
    _start = time.time()
    for record in invalid_data:
        try:
            deserialize_function(record)
        except:
            pass
    results.invalid_data_processing = time.time() - _start

    results.total = time.time() - start
    return results


def main() -> None:
    valid_data, invalid_data = get_data()
    results = [
        run_benchmark(
            'attrs', valid_data, invalid_data, lambda record: AttrsParent(**record),
            lambda instance: asdict(instance)
        ),
        run_benchmark(
            'pydantic', valid_data, invalid_data, lambda record: PydanticParent(**record),
            lambda instance: instance.dict()
        ),
        run_benchmark(
            'pymodelio', valid_data, invalid_data, lambda record: PymodelioParent.from_dict(record),
            lambda instance: instance.to_dict()
        )
    ]

    for result in results:
        print(f'\n{result.name} results:\n{result}')


if __name__ == '__main__':
    main()
```

You can update the variables `NUM_PARENTS` and `NUM_CHILDREN_PER_PARENT` for adjusting the amount of data you want to run the benchmark for (be careful about increasing the numbers too much because this will cause an exponential growth).

The results of this benchmark executed in a _Manjaro Linux_ with an _AMD Ryzen 7 PRO 4750U_ proccessor and _16GB_ of ram, using _Python 3.10_ were:

```
Creating sample data

Starting attrs benchmark...

Starting pydantic benchmark...

Starting pymodelio benchmark...

attrs results:
Total 1.2478992938995361 seconds:
  > Valid data processing (total 0.9774622917175293 seconds)
     - Deserialization 0.26752424240112305 seconds
     - Serialization 0.7099277973175049 seconds
  > Attributes updating (total 0.9774622917175293 seconds)
  > Invalid data processing (total 0.0004627704620361328 seconds)


pydantic results:
Total 3.9808452129364014 seconds:
  > Valid data processing (total 1.9142224788665771 seconds)
     - Deserialization 0.8401687145233154 seconds
     - Serialization 1.074042558670044 seconds
  > Attributes updating (total 1.9142224788665771 seconds)
  > Invalid data processing (total 1.808525800704956 seconds)


pymodelio results:
Total 1.9439215660095215 seconds:
  > Valid data processing (total 1.2387640476226807 seconds)
     - Deserialization 0.9972996711730957 seconds
     - Serialization 0.2414543628692627 seconds
  > Attributes updating (total 1.2387640476226807 seconds)
  > Invalid data processing (total 0.5468699932098389 seconds)
```

First of all, it's important to know that in this benchmark, we implemented a case of use that can be easily implemented by using any of the three compared libraries. But there are some cases (as we described earlier in this doc) that can not be easily implemented with _attrs_ or _pydantic_.

So now we can continue...

#### attrs

As we can see, _attrs_ is the most performing library of the three, but at what cost? Well, for the _attrs_ models we had to manually specify the validators and also implement one for `children`. Apart from this, we had to implement the converter for the deserialization process of `children`.

#### pydantic

_pydantic_ performed a bit better than pymodelio in terms of deserialization, but when we analyze the total time or the other evaluated topics, there was a big difference with the other two.

It's important to mention that pydantic perform validations each time an attribute is updated. Pymodelio doesn't share that philosophy, instead, you can trigger the validations whenever you want by calling the `validate()` method of any pymodelio's model.

#### pymodelio

As we can see _pymodelio_ got a punctuation in the middle between _attrs_ and _pydantic_.

In terms of deserialization, _pymodelio_ performed a bit worse than _pydantic_, but outperformed it in all other topics. Regarding serialization, pymodelio was the best of the three.

#### Conslusions

This benchmark was implemented for doing mainly performance comparisons. But don't forget that performance is not always the most important topic to consider when choosing a library like these ones.

When you have a large project to maintain with multiple people working on the same codebase, usability is often an excellent point to choose one option over the others.

So not only consider the numbers here, _attrs_ and _pydantic_ are great libraries that have been there for a long time. One does things that the other doesn't. We hope some day _pymodelio_ will also be another popular option, not to replace the others, but to complement them when they don't suit your needs or your coding style.
