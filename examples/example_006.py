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
