from typing import Any

import pytest

from pymodelio import BaseModel
from pymodelio.attribute import Attribute
from pymodelio.constants import UNDEFINED
from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.model import pymodelio_model
from tests.test_models.computer import Computer


def test_valid_model_hierarchy():
    data = {
        'serial_no': 'computer-001',
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
    }
    computer = Computer.from_dict(data)
    assert computer.serial_no == data['serial_no']


def test_invalid_submodel_as_child():
    data = {
        'serial_no': 'computer-001',
        'cpu': {
            'frequency': '3500',
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
    }
    with pytest.raises(ModelValidationException) as ex_info:
        Computer.from_dict(data)
    assert ex_info.value.args[0] == 'Computer.cpu.frequency is not a valid int'


def test_invalid_submodel_in_list_as_child():
    data = {
        'serial_no': 'computer-001',
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
                'size': '512'
            }
        ]
    }
    with pytest.raises(ModelValidationException) as ex_info:
        Computer.from_dict(data)
    assert ex_info.value.args[0] == 'Computer.disks[1].size is not a valid int'


def test_can_not_init_non_initable_model_attributes():
    @pymodelio_model
    class Model:
        non_initable_model_attr: Attribute[str](initable=False, default_factory=lambda: 'default value')

    with pytest.raises(NameError) as ex_info:
        Model(non_initable_model_attr='custom value')
    assert ex_info.value.args[0] == 'non_initable_model_attr attribute is not initable for class Model'


def test_model_init_uses_default_factory_value_when_provided_value_is_UNDEFINED():
    @pymodelio_model
    class Model:
        model_attr: Attribute[int](default_factory=lambda: 12345)

    model = Model(model_attr=UNDEFINED)
    assert model.model_attr == 12345


def test_model_initialization_sets_private_attribute():
    @pymodelio_model
    class Model:
        __private_attr_1: Attribute[int]

        @property
        def private_attr_1(self) -> int:
            return self.__private_attr_1

    @pymodelio_model
    class ChildModel(Model):
        __private_attr_2: Attribute[str]

        @property
        def private_attr_2(self) -> int:
            return self.__private_attr_2

    model = ChildModel(private_attr_1=12345, private_attr_2='asd')
    assert model.private_attr_1 == 12345
    assert model.private_attr_2 == 'asd'


def test_to_dict_serializes_public_model_attributes():
    data = {
        'serial_no': 'computer-001',
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
    }
    computer = Computer.from_dict(data)
    assert computer.to_dict() == {
        'cpu': {
            'cores': 8,
            'frequency': 3500,
            'serial_no': computer.cpu.serial_no
        },
        'disks': [
            {
                'serial_no': computer.disks[0].serial_no,
                'size': 1024
            },
            {
                'serial_no': computer.disks[1].serial_no,
                'size': 512
            }
        ],
        'rams': [
            {
                'frequency': 1600,
                'serial_no': computer.rams[0].serial_no,
                'size': 8
            },
            {
                'frequency': 1800,
                'serial_no': computer.rams[1].serial_no,
                'size': 16
            }
        ],
        'serial_no': 'computer-001'
    }


def test_model_calls_when_validating_attr_method_when_performing_attribute_validations():
    @pymodelio_model
    class Model:
        model_attr: Attribute[str]

        @classmethod
        def _when_validating_attr(cls, internal_attr_name: str, exposed_attr_name: str, attr_value: Any,
                                  attr_path: str, parent_path: str, pymodel_attribute: Attribute) -> None:
            if exposed_attr_name == 'model_attr' and attr_value != 'Hello world':
                raise ModelValidationException(f'{attr_path} does not match "Hello world"')

    with pytest.raises(ModelValidationException) as ex_info:
        Model(model_attr='custom value')
    assert ex_info.value.args[0] == 'Model.model_attr does not match "Hello world"'


def test_model_definition_using_inheritance_from_base_model():
    class ParentModel(BaseModel):
        parent_attr: Attribute[int]

    class ChildModel(ParentModel):
        child_attr: Attribute[str]

    model = ChildModel(parent_attr=12345, child_attr='asd')
    assert model.parent_attr == 12345
    assert model.child_attr == 'asd'
