import pytest

from src.exceptions.model_validation_exception import ModelValidationException
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
