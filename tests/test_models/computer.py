import uuid
from typing import List

from pymodelio.attribute import Attribute
from pymodelio.constants import UNDEFINED
from pymodelio.model import pymodelio_model
from pymodelio.validators.int_validator import IntValidator
from pymodelio.validators.iterable_validator import IterableValidator
from pymodelio.validators.validator import Validator


@pymodelio_model
class Component:
    __serial_no: Attribute[str](default_factory=lambda: uuid.uuid4().__str__())

    @property
    def serial_no(self) -> str:
        return self.__serial_no


@pymodelio_model
class CPU(Component):
    _frequency: Attribute[int](validator=IntValidator())
    cores: Attribute[int](validator=IntValidator())

    @property
    def frequency(self) -> int:
        return self._frequency

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
    _cpu: Attribute[CPU](validator=Validator(expected_type=CPU))
    _rams: Attribute[List[RAM]](validator=IterableValidator(elements_type=RAM))
    _disks: Attribute[List[Disk]](validator=IterableValidator(elements_type=Disk))

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
