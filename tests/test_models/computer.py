import uuid
from typing import List

from pymodelio import PymodelioModel
from pymodelio.attribute import Attr
from pymodelio.constants import UNDEFINED
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
    cores: Attr(int, validator=IntValidator(min_value=0))

    @property
    def frequency(self) -> int:
        return self._frequency

    @staticmethod
    def deserialize_from_dict(data: dict, auto_validate: bool = True) -> 'CPU':
        return CPU(
            frequency=data.get('frequency'),
            cores=data.get('cores'),
            auto_validate=auto_validate
        )


class RAM(Component):
    frequency: Attr(int, validator=IntValidator(min_value=0))
    size: Attr(int, validator=IntValidator(min_value=0))

    @staticmethod
    def deserialize_from_dict(data: dict, auto_validate: bool = True) -> 'RAM':
        return RAM(
            frequency=data.get('frequency'),
            size=data.get('size'),
            auto_validate=auto_validate
        )


class Disk(Component):
    size: Attr(int, validator=IntValidator(min_value=0))

    @staticmethod
    def deserialize_from_dict(data: dict, auto_validate: bool = True) -> 'Disk':
        return Disk(
            size=data.get('size'),
            auto_validate=auto_validate
        )


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

    @staticmethod
    def deserialize_from_dict(data: dict, auto_validate: bool = True) -> 'Computer':
        return Computer(
            serial_no=data.get('serial_no') if 'serial_no' in data else UNDEFINED,
            cpu=CPU.deserialize_from_dict(data.get('cpu'), auto_validate=False),
            rams=[RAM.deserialize_from_dict(x, auto_validate=False) for x in data.get('rams')],
            disks=[Disk.deserialize_from_dict(x, auto_validate=False) for x in data.get('disks')],
            auto_validate=auto_validate
        )
