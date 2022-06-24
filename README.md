[![Python tests](https://github.com/GabrielMartinMoran/pymodelio/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/GabrielMartinMoran/pymodelio/actions/workflows/python.yml)
[![codecov](https://codecov.io/gh/GabrielMartinMoran/pymodelio/branch/main/graph/badge.svg?token=VVKW3GDMLD)](https://codecov.io/gh/GabrielMartinMoran/pymodelio)

# pymodelio
A simple Python module for performing model validations

## How to use the module

### Declaring the models

```py
@pymodelio_model
class Component:
    __serial_no: Attribute[str](default_factory=lambda: uuid.uuid4().__str__())


@pymodelio_model
class CPU(Component):
    frequency: Attribute[int](validator=IntValidator())
    cores: Attribute[int](validator=IntValidator())

    @staticmethod
    def from_dict(data: dict, auto_validate: bool = True) -> 'CPU':
        return CPU(
            frequency=data.get('frequency'),
            cores=data.get('cores'),
            auto_validate=auto_validate
        )


@pymodelio_model
class RAM(Component):
    frequency: Attribute[int](validator=IntValidator())
    size: Attribute[int](validator=IntValidator())

    @staticmethod
    def from_dict(data: dict, auto_validate: bool = True) -> 'RAM':
        return RAM(
            frequency=data.get('frequency'),
            size=data.get('size'),
            auto_validate=auto_validate
        )


@pymodelio_model
class Disk(Component):
    size: Attribute[int](validator=IntValidator())

    @staticmethod
    def from_dict(data: dict, auto_validate: bool = True) -> 'Disk':
        return Disk(
            size=data.get('size'),
            auto_validate=auto_validate
        )


@pymodelio_model
class Computer(Component):
    _cpu: Attribute[CPU](validator=NestedModelValidator())
    _rams: Attribute[List[RAM]](validator=NestedModelListValidator())
    _disks: Attribute[List[Disk]](validator=NestedModelListValidator())

    @property
    def serial_no(self) -> str:
        return self.__serial_no

    @property
    def cpu(self) -> CPU:
        return self._cpu

    @property
    def rams(self) -> List[RAM]:
        return self._rams

    @property
    def disks(self) -> List[Disk]:
        return self._disks

    @staticmethod
    def from_dict(data: dict, auto_validate: bool = True) -> 'Computer':
        return Computer(
            serial_no=data.get('serial_no') if 'serial_no' in data else UNDEFINED,
            cpu=CPU.from_dict(data.get('cpu'), auto_validate=False),
            rams=[RAM.from_dict(x, auto_validate=False) for x in data.get('rams')],
            disks=[Disk.from_dict(x, auto_validate=False) for x in data.get('disks')],
            auto_validate=auto_validate
        )

```

### Using the models
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

## Considerations
When a class attribute has the annotation `Attribute[\<type\>]`, it will be transformed into an instance attribute during the model initialization.


When defining a protected or private model attribute with underscore or double underscore respectively, if that property can be set by the model constructor, it's value will be obtained from an attribute with the same name but without underscores. For instance:
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

print(component.serial_no) # It will print '123e4567-e89b-12d3-a456-426614174000'
print(component.model_name) # It will print 'ABC123'
```

## Available validators

### Validator
Other validators inherit from this one.
```py
Validator(nullable: bool = False, message: str = None)
```

### StringValidator
```py
StringValidator(min_len: int = 0, max_len: int = math.inf, fixed_len: int = None, regex: str = None, nullable: bool = False, message: str = None)
```

### NumericValidator
```py
NumericValidator(expected_type: type, min_value: Number = -math.inf, max_value: Number = math.inf, nullable: bool = False, message: str = None)
```

### IntValidator
A subclass of NumericValidator specific for integers.
```py
IntValidator(min_value: Number = -math.inf, max_value: Number = math.inf, nullable: bool = False, message: str = None)
```

### FloatValidator
A subclass of NumericValidator specific for float numbers.
```py
FloatValidator(min_value: Number = -math.inf, max_value: Number = math.inf, nullable: bool = False, message: str = None)
```

### DatetimeValidator
```py
DatetimeValidator(nullable: bool = False, message: str = None)
```

### NestedModelValidator
A validator for nested models. Validated value must implement `validate` method in order to be considered a model by this validator.
```py
NestedModelValidator(nullable: bool = False, message: str = None)
```

### NestedModelListValidator
A validator for nested model lists. Validated list elements must implement `validate` method in order to be considered a model by this validator.
```py
NestedModelValidator(nullable: bool = False, message: str = None)
```
