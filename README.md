[![Python v3.8+](https://img.shields.io/badge/Python-v3.8%2B-blue)](https://www.python.org/downloads)
[![Python tests](https://github.com/GabrielMartinMoran/pymodelio/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/GabrielMartinMoran/pymodelio/actions/workflows/python.yml)
[![codecov](https://codecov.io/gh/GabrielMartinMoran/pymodelio/branch/main/graph/badge.svg?token=VVKW3GDMLD)](https://codecov.io/gh/GabrielMartinMoran/pymodelio)

# pymodelio

A simple Python module for defining domain models, serializing, deserializing and validating them.

## What is this module for?

Have you ever needed to validate a user input, the body of a request, data obtained from a service like a database or
an external api, without needing to define serializers and deserializers for your class nested data structure?
Well, that's what `pymodelio` is built for, simplicity when defining your domain models and the surrounding
restrictions.

## How to install the module

Installing the module is simple as running the following script on your terminal:

```shell
pip install -U pymodelio
```

## How to use the module

### Declaring the models

Pymodelio models are declared by inheriting from `PymodelioModel` class. When instantiating a model, all _initable_
declared attributes should be provided (if not, default generated from _default_factory_ builders will be used instead).

**Let's begin with a simple example**

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
*IMPORTANT NOTE:* Note that pymodelio attributes are defined by using Python type annotations, so we are not setting dafault values to static class attributes. Also, when you interact with these attibutes, the code autocompletion engine is going to autocomplete with the methods and properties of attribute type you specified as the first parameter of `Attr` (because on runtime you will be really working with that attribute type). For instance when interacting with `name` inside of the class, that prop will we considered as a `str`.

**What about using models from other models?**

```py
from datetime import datetime
from typing import Optional
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

**What about using a model within the same model?**

For doing this, we need to use [forward references](https://peps.python.org/pep-0484/#forward-references) when using the `Person` model, because it was not yet initialized during the attribute declaration.

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

**Let's continue with a more complex example?**

```py
import uuid
from typing import List
from pymodelio import Attr, PymodelioModel
from pymodelio.validators import ListValidator, StringValidator
from pymodelio.validators.int_validator import IntValidator
from pymodelio.validators.validator import Validator



class Component(PymodelioModel):
    __serial_no: Attr(str,
        validator=StringValidator(fixed_len=36, regex=r'^[a-z0-9-]+$'),
        default_factory=lambda: uuid.uuid4().__str__()
    )

    @property
    def serial_no(self) -> str:
        return self.__serial_no


class CPU(Component):
    _frequency: Attr(int, validator=IntValidator(min_value=0))
    cores: Attr(int, validator=IntValidator(min_value=0))

    @property
    def frequency(self) -> int:
        return self._frequency


class RAM(Component):
    frequency: Attr(int, validator=IntValidator(min_value=0))
    size: Attr(int, validator=IntValidator(min_value=0))


class Disk(Component):
    size: Attr(int, validator=IntValidator(min_value=0))


class Computer(Component):
    _cpu: Attr(CPU, validator=Validator(expected_type=CPU))
    _rams: Attr(List[RAM], validator=ListValidator(elements_type=RAM, allow_empty=False))
    _disks: Attr(List[Disk], validator=ListValidator(elements_type=Disk))

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
```

Also, instead of initializing a models using their constructors, we can deserialize them from python dictionaries by calling `from_dict` factory constructor.

```py
computer = Computer.from_dict({
    'serial_no': '123e4567-e89b-12d3-a456-426614174000',
    'cpu': {
        'frequency': 3500,
        'cores': 8
    },
    'rams': [
        {
            'frequency': 1600,
            'size': 8
        },
        {
            'frequency': 1800,
            'size': 16
        }
    ],
    'disks': [
        {
            'size': 1024
        },
        {
            'size': 512
        }
    ]
})
```

**Wait a second, what is happening here?**

You probably noticed that in the example above, there are some protected and private attributes that are being set by
providing their names without underscores.

**Why is it doing that?**

Some known Python modules that do similar things like pymodelio forces you to specify the protected or private
attributes by passing some parameter in the type or validator description. The idea of pymodelio is to let you use the
language conventions for defining that without losing the capability of automatically handling initialization if you
want that.

This module hugs the open/closed principle by allowing you to not define all your attributes public, but also letting
you initialize them in their public form (based on python code writing conventions).

**Wait! I don't want that! how can I disable it?**

You can always specify which attributes are not exposed by the constructor using their public form by passing the
parameter `initable=False` to the Attribute constructor.

Also, there is a global way of disabling this behaviour. You can configure `PymodelioSettings` for avoiding unwanted
behaviours in this way:

```py
from pymodelio import PymodelioSettings
from pymodelio import PymodelioSetting

# This line will disable automatic protected attributes initialization (all attributes that start with '_')
PymodelioSettings.set(PymodelioSetting.INIT_PROTECTED_ATTRS_BY_DEFAULT, False)

# This line will disable automatic private attributes initialization (all attributes that start with '__')
PymodelioSettings.set(PymodelioSetting.INIT_PRIVATE_ATTRS_BY_DEFAULT, False)
```

In case you want to get a value of a `PymodelioSetting`, you can do this:

```py
from pymodelio import PymodelioSettings
from pymodelio import PymodelioSetting

PymodelioSettings.get(PymodelioSetting.INIT_PROTECTED_ATTRS_BY_DEFAULT)  # True by default

PymodelioSettings.get(PymodelioSetting.INIT_PRIVATE_ATTRS_BY_DEFAULT)  # True by default
```

**Let's talk about attribute's validation**

Other great principle where this module is stood on, is that an instance of a domain model shouldn't exist if it is not
valid. For ensuring that, pymodelio automatically validates the instantiated models if you don't specify the opposite (
by passing the parameter `auto_validate=False`). So have in mind that for performance improvements, we could disable
auto validation in nested models initialization when using the constructor way of instantiating the `Computer` because
when the parent validator is called, it will validate the whole structure. Here you have the modified code:

```py
computer = Computer(
    serial_no='123e4567-e89b-12d3-a456-426614174000',
    cpu=CPU(frequency=3500, cores=8, auto_validate=False),
    rams=[RAM(frequency=1600, size=8, auto_validate=False), RAM(frequency=1800, size=16, auto_validate=False)],
    disks=[Disk(size=1024, auto_validate=False), Disk(size=512, auto_validate=False)]
)
```

You can also pass this parameter for preventing automatic validations to the `from_dict` factory constructor, like this:

```py
computer = Computer.from_dict({
    'serial_no': '123e4567-e89b-12d3-a456-426614174000',
    'cpu': {'frequency': 3500, 'cores': 8},
    'rams': [{'frequency': 1600, 'size': 8}, {'frequency': 1800, 'size': 16}],
    'disks': [{'size': 1024}, {'size': 512}]
}, auto_validate=False)
```

Other thing that differentiates pymodelio from other modules that have a similar job, is that when you use pymodelio,
you have available a lot of already implementing validators that simplifies most cases like validating an email, the
length of a string, the range of a number, the emptiness of a list, etc. Even if a validator is not already implemented,
you can do it in a very easy way by inheriting from `Validator` class or using some exposed middleware model
initialization methods. If you are interested on this, please scroll down until you find the _validation_ section.

### Customizing the model's initialization workflow

```py
class Model(PymodelioModel):
    model_attr: Attr(str)

    def __before_init__(self, *args, **kwargs) -> None:
        # This method is called before any other method when the model constructor is called
        # It receives the same parameters the constructor gets
        pass

    def __before_validate__(self) -> None:
        # This method is called after initializing the model attributes but just before
        # performing the model validations (it will be executed even if
        # auto_validate = False)
        pass

    def __once_validated__(self) -> None:
        # This method is called just after performing the model validations initializing
        # the model attributes but before performing the model validations (it will be
        # executed even if auto_validate = False)
        pass
```

### Non initable attributes

```py
class Model(PymodelioModel):
    non_initable_model_attr: Attr(str, initable=False, default_factory=lambda: 'Non initable default value')


# WARNING: This will raise a NameError('non_initable_model_attr attribute is not
#          initable for class Model')
Model(non_initable_model_attr='custom value')


```

## Considerations

When instantiating a model specifying `auto_validate = False`, the model won't be automatically validated during
initialization.

When a class attribute has the annotation `Attr(<type>)`, it will be transformed into an instance attribute during
the model initialization.

When defining a protected or private model attribute with underscore or double underscore respectively, if that property
can be set by the model constructor, it's value will be obtained from an attribute with the same name but without
underscores. For instance:

```py
class Component(PymodelioModel):
    __serial_no: Attr(str)
    _model_name: Attr(str)

    @property
    def serial_no(self) -> str:
        return self.__serial_no

    @property
    def model_name(self) -> str:
        return self._model_name


component = Component(serial_no='123e4567-e89b-12d3-a456-426614174000', model_name='ABC123')

print(component.serial_no)  # It will print '123e4567-e89b-12d3-a456-426614174000'
print(component.model_name)  # It will print 'ABC123'
```

As we mentioned before, this default behavior can be disabled by configuring `PymodelioSettings`.

## Validation

### Customizing the validation process

Custom validators can be implemented by inheriting from the `Validator` class. Even that, there is also other way of
performing custom validations that consists on implementing `_when_validating_attr` method in the defined model. This
method is called after the attribute validator is called (if the attribute does not have a validator, this method is
called anyway).

```py
def _when_validating_attr(self, internal_attr_name: str, exposed_attr_name: str, attr_value: Any, attr_path: str,
                          parent_path: str, attr: PymodelioAttr) -> None:
    pass
```

## Available validators

### Validator

A generic validator for any type passed by parameter. It is also capable of validating other models. Validated value
must implement `validate` method in order to be considered a model by this validator.
Other validators inherit from this one.

```py
Validator(expected_type: Union[type, List[type]] = None, nullable: bool = False, message: Optional[str] = None)
```

### StringValidator

```py
StringValidator(min_len: Optional[int] = None, max_len: Optional[int] = None, fixed_len: Optional[int] = None, regex:
Optional[str] = None, nullable: bool = False, message: Optional[str] = None)
```

### NumericValidator

```py
NumericValidator(expected_type: type, min_value: Optional[Number] = None, max_value: Optional[
    Number] = None, expected_type: Union[type, List[type]] = None, nullable: bool = False, message: Optional[
    str] = None)
```

### IntValidator

A subclass of NumericValidator specific for integers.

```py
IntValidator(min_value: Optional[int] = None, max_value: Optional[int] = None, nullable: bool = False, message:
Optional[str] = None)
```

### FloatValidator

A subclass of NumericValidator specific for float numbers.

```py
FloatValidator(min_value: Optional[float] = None, max_value: Optional[float] = None, nullable: bool = False, message:
Optional[str] = None)
```

### DatetimeValidator

```py
DatetimeValidator(nullable: bool = False, message: Optional[str] = None)
```

### DictValidator

```py
DictValidator(nullable: bool = False, message: Optional[str] = None)
```

### IterableValidator

A validator for an of any type that allows nested models. Validated children must implement `validate` method in
order to be considered a model by this validator.

```py
IterableValidator(expected_type: Union[type, List[type]] = None, elements_type: Union[
    type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message: Optional[str] = None)
```

### ListValidator

A subclass of IterableValidator specific for lists.

```py
ListValidator(elements_type: Union[type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message:
Optional[str] = None)
```

### SetValidator

A subclass of IterableValidator specific for sets.

```py
SetValidator(elements_type: Union[type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message:
Optional[str] = None)
```

### TupleValidator

A subclass of IterableValidator specific for tuples.

```py
TupleValidator(elements_type: Union[type, List[type]] = None, allow_empty: bool = True, nullable: bool = False, message:
Optional[str] = None)
```

### EmailValidator

```py
EmailValidator(nullable: bool = False, message: Optional[str] = None)
```

### BoolValidator

```py
BoolValidator(nullable: bool = False, message: Optional[str] = None)
```

### ForwardRefValidator

A validator used for forwarded references (see `typing.ForwardRef` for more info in `typing` module documentation). The expected type of the validator is intended to be always a _PymodelioModel_ and it's obtained when validating the attribute the first time.

```py
ForwardRefValidator(ref: ForwardRef, nullable: bool = False, message: Optional[str] = None)
```

## Serialization and de-serialization

For serialization, pymodelio models implement a `to_dict()` method that serializes the public attributes and
properties (defined using the `property` decorator). For the example at the beginning of this documentation,
calling `to_dict()` method in a computer's instance returns something like:

```py
{
    'cpu': {
        'cores': 8,
        'frequency': 3500,
        'serial_no': '0f3b6ef1-dea3-4cdd-be53-ef85079731c4'
    },
    'disks': [
        {
            'serial_no': '011639e0-82dd-44c0-ba46-3580482c0add',
            'size': 1024
        },
        {
            'serial_no': 'd76474eb-b854-49d1-a0df-917fe8526621',
            'size': 512
        }
    ],
    'rams': [
        {
            'frequency': 1600,
            'serial_no': '8a2639e0-aa0c-450a-8ee1-8dd536578bb8',
            'size': 8
        },
        {
            'frequency': 1800,
            'serial_no': '49140714-263e-4fbb-b366-06916c4e81f5',
            'size': 16
        }
    ],
    'serial_no': 'computer-001'
}
```

If a defined model implements `to_dict()` method, this overridden one will be used instead of the default
one. The signature for overriding this method should be:

```py
def to_dict(self) -> dict:
    return {}  # Returns the serialized model

```

In case of properties (defined using the `property` decorator) that you don't want to serialize, you can use the
`@do_not_serialize` decorator like this:

```py
class Person(PymodelioModel):
    _name: Attr(str)

    @property
    def name(self) -> str:
        return self._name

    @property
    @pymodelio.do_not_serialize
    def lowercase_name(self) -> str:
        # This property won't be automatically serialized
        return self._name.lower()
```

For de-serialization, pymodelio models implement a `from_dict()` factory constructor that as it name says, it can be
used
for decoding python dictionaries into model instances as used in the first example shown. As `to_dict()`, `from_dict()`
can also be implemented by a model and in that case, the model one will be used instead. The signature for overriding
this method should be:

```py
@classmethod
def from_dict(cls, data: dict, auto_validate: bool = True) -> CustomModel:
    return CustomModel(**data)  # Replace CustomModel with your model and call the constructor as you need
```

## Configuring Pymodelio settings

As we mentioned before, there are some settings that can be configured by calling the `PymodelioSettings` class. These settigs and their expected types are:

- **PymodelioSetting.INIT_PROTECTED_ATTRS_BY_DEFAULT** (`bool`): If `True`, all initable protected attributes will be exposed in the constructor on their public form. For instance: `_name` will be exposed as `name`.
- **PymodelioSetting.INIT_PRIVATE_ATTRS_BY_DEFAULT** (`bool`): If `True`, all initable private attributes will be exposed in the constructor on their public form. For instance: `__id` will be exposed as `id`.
- **PymodelioSetting.USE_CACHE_OPTIMIZATIONS** (`bool`): If `True`, pymodelio will use a cache for some performance tweaks. Disable it if you want to re-define model classes using the same under the same scope.
- **PymodelioSetting.AUTO_PARSE_DATES_AS_UTC** (`bool`): If `True`, deserialized dates will be considered `UTC`.
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

## Let's compare the same code using raw python against using pymodelio

For this comparison, we are not implementing serialization and de-serialization in the raw Python models (pymodelio
handles this automatically for its models).

### Using raw python

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

### Using pymodelio

pymodelio model validation errors also give more information about the full path of nested structures. In case of lists,
including the index of the list element where the error occurred.

```py
class PymodelioChildModel(PymodelioModel):
    public_child_attr: Attr(int)


class PymodelioParentModel(PymodelioModel):
    public_attr: Attr(int, validator=IntValidator(min_value=0, max_value=10))
    _protected_attr: Attr(str, validator=StringValidator(fixed_len=5, regex='^[A-Z]+$'))  # Only capitalized chars
    __private_attr: Attr(datetime)
    child_model_attr: Attr(PymodelioChildModel)
    children_model_attr: Attr(List[PymodelioChildModel])
    optional_attr: Attr(dict, default_factory=dict)
    non_initable_attr: Attr(List[str], initable=False, default_factory=list)

```
