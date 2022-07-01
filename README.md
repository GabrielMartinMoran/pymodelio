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
pip install pymodelio
```

## How to use the module

### Declaring the models

Models can be declared using the `pymodelio_model` decorator or by inheriting from `BaseModel`. In the example below,
the decorator way it's used for not complicating the inheritance tree, but it would be the same if instead of using the
decorator in each model, we just declare `Component` class as `class Component(BaseModel)`.

```py
import uuid
from typing import List

from pymodelio.attribute import Attribute
from pymodelio.model import pymodelio_model
from pymodelio.validators import ListValidator, StringValidator
from pymodelio.validators.int_validator import IntValidator
from pymodelio.validators.validator import Validator


@pymodelio_model
class Component:
    __serial_no: Attribute[str](
        validator=StringValidator(fixed_len=36, regex=r'^[a-z0-9-]+$'),
        default_factory=lambda: uuid.uuid4().__str__()
    )

    @property
    def serial_no(self) -> str:
        return self.__serial_no


@pymodelio_model
class CPU(Component):
    _frequency: Attribute[int](validator=IntValidator(min_value=0))
    cores: Attribute[int](validator=IntValidator(min_value=0))

    @property
    def frequency(self) -> int:
        return self._frequency


@pymodelio_model
class RAM(Component):
    frequency: Attribute[int](validator=IntValidator(min_value=0))
    size: Attribute[int](validator=IntValidator(min_value=0))


@pymodelio_model
class Disk(Component):
    size: Attribute[int](validator=IntValidator(min_value=0))


@pymodelio_model
class Computer(Component):
    _cpu: Attribute[CPU](validator=Validator(expected_type=CPU))
    _rams: Attribute[List[RAM]](validator=ListValidator(elements_type=RAM, allow_empty=False))
    _disks: Attribute[List[Disk]](validator=ListValidator(elements_type=Disk))

    @property
    def cpu(self) -> CPU:
        return self._cpu

    @property
    def rams(self) -> List[RAM]:
        return self._rams

    @property
    def disks(self) -> List[Disk]:
        return self._disks
```

### Let's use these models

You can do it by using the class constructors

```py
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

Or you can call `from_dict` factory constructor for instantiating the models by deserializing a python dictionary

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

### Wait a second, what is happening here?

You probably noticed that in the example above, there are some protected and private attributes that are being set by
providing their names without underscores.

**Why is it doing that?**

Some known Python modules that do similar things like pymodelio forces you to specify the protected or private
attributes by passing some parameter in the type or validator description. The idea of pymodelio is to let you use the
language conventions for defining that without losing the capability of automatically handling initialization if you
want that.

You can always specify which attributes are not exposed by the constructor using their public form by passing the
parameter `initable=False` to the Attribute constructor.

This module hugs the open/closed principle by allowing you to not define all your attributes public, but also letting
you initialize them in their public form (based on python code writing conventions).

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
initialization methods. If you are interested on this, please scroll down until you find the *validation* section.

### Customizing the model's initialization workflow

```py
@pymodelio_model
class Model:
    model_attr: Attribute[str]

    @classmethod
    def __before_init__(cls, *args, **kwargs) -> None:
        # This method is called before everything when the model constructor is called
        # It receives the same parameters the constructor gets
        pass

    @classmethod
    def __before_validate__(cls) -> None:
        # This method is called after initializing the model attributes but just before
        # performing the model validations (it will be executed even if 
        # auto_validate = False)
        pass

    @classmethod
    def __once_validated__(cls) -> None:
        # This method is called just after performing the model validations initializing
        # the model attributes but before performing the model validations (it will be
        # executed even if auto_validate = False)
        pass
```

### Non initable attributes

```py
@pymodelio_model
class Model:
    non_initable_model_attr: Attribute[str](initable=False, default_factory=lambda: 'Non initable default value')


# WARNING: This will raise a NameError('non_initable_model_attr attribute is not
#          initable for class Model')
Model(non_initable_model_attr='custom value')


```

## Considerations

When instantiating a model specifying `auto_validate = False`, the model won't be automatically validated during
initialization.

When a class attribute has the annotation `Attribute[<type>]`, it will be transformed into an instance attribute during
the model initialization.

When defining a protected or private model attribute with underscore or double underscore respectively, if that property
can be set by the model constructor, it's value will be obtained from an attribute with the same name but without
underscores. For instance:

```py
@pymodelio_model
class Component:
    __serial_no: Attribute[str]
    _model_name: Attribute[str]

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

## Validation

### Customizing the validation process

Custom validators can be implemented by inheriting from the `Validator` class. Even that, there is also other way of
performing custom validations that consists on implementing `_when_validating_attr` method in the defined model. This
method is called after the attribute validator is called (if the attribute does not have a validator, this method is
called anyway).

```py
def _when_validating_attr(self, internal_attr_name: str, exposed_attr_name: str, attr_value: Any, attr_path: str,
                          parent_path: str, pymodel_attribute: Attribute) -> None:
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

### EmailValidator

```py
EmailValidator(nullable: bool = False, message: Optional[str] = None)
```

### BoolValidator

```py
BoolValidator(nullable: bool = False, message: Optional[str] = None)
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
        assert isinstance(self.public_child_attr, int), 'public_child_attr is not a valid int'


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
        assert isinstance(self.public_attr, int), 'public_child_attr is not a valid int'
        assert self.public_attr >= self._PUBLIC_ATTR_MIN_VALUE,
        f'public_child_attr is lower than {self._PUBLIC_ATTR_MIN_VALUE}'

        assert self.public_attr <= self._PUBLIC_ATTR_MAX_VALUE,
        f'public_child_attr is greater than {self._PUBLIC_ATTR_MAX_VALUE}'

        assert isinstance(self._protected_attr, str), '_protected_attr is not a valid str'
        assert len(self._protected_attr) == self._PROTECTED_ATTR_FIXED_LENGTH,
        f'_protected_attr length is different than {self._PROTECTED_ATTR_FIXED_LENGTH}'
        assert re.compile(self._PROTECTED_ATTR_REGEX).match(self._protected_attr) is not None,
        '_protected_attr does not match configured regex'

        assert isinstance(self.child_model_attr, RawPythonChildModel),
        'child_model_attr is not a valid RawPythonChildModel'
        self.child_model_attr.validate()

        assert isinstance(self.children_model_attr, list), 'children_model_attr is not a valid list'
        for child_model in self.children_model_attr:
            child_model.validate()

        assert isinstance(self.__private_attr, datetime), '__private_attr is not a valid datetime'
        
        assert isinstance(self.optional_attr, dict), 'optional_attr is not a valid dict'
```

### Using pymodelio

pymodelio model validation errors also give more information about the full path of nested structures. In case of lists,
including the index of the list element where the error occurred.

```py
@pymodelio_model
class PymodelioChildModel:
    public_child_attr: Attribute[int](validator=IntValidator())


@pymodelio_model
class PymodelioModel:
    public_attr: Attribute[int](validator=IntValidator(min_value=0, max_value=10))
    _protected_attr: Attribute[str](validator=StringValidator(fixed_len=5, regex='^[A-Z]+$'))  # Only capitalized chars
    __private_attr: Attribute[datetime](validator=DatetimeValidator())
    child_model_attr: Attribute[PymodelioChildModel](validator=Validator(expected_type=PymodelioChildModel))
    children_model_attr: Attribute[List[PymodelioChildModel]](
        validator=ListValidator(elements_type=PymodelioChildModel))
    optional_attr: Attribute[dict](validator=DictValidator())
    non_initable_attr: Attribute[List[str]](initable=False, default_factory=list)
```