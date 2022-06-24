import uuid
from typing import List

from src.attribute import Attribute
from src.model import pymodelio_model, UNDEFINED
from src.validators.int_validator import IntValidator
from src.validators.nested_model_list_validator import NestedModelListValidator
from src.validators.nested_model_validator import NestedModelValidator


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
