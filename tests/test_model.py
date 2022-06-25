import pytest

from src.attribute import Attribute
from src.constants import UNDEFINED
from src.exceptions.model_validation_exception import ModelValidationException
from src.model import pymodelio_model
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
    assert ex_info.value.args[0] == 'Computer._cpu.frequency is not a valid int'


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
    assert ex_info.value.args[0] == 'Computer._disks[1].size is not a valid int'


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
