import pymodelio
from pymodelio import Attribute
from tests.test_models.computer import Computer


def test_to_dict_serializes_public_model_attributes():
    data = {
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
    }
    computer = Computer.deserialize_from_dict(data)
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
        'serial_no': '123e4567-e89b-12d3-a456-426614174000'
    }


def test_to_dict_does_not_serialize_properties_marked_with_do_not_serialize_decorator():
    @pymodelio.model
    class TestCaseModel:
        _name: Attribute[str]()

        @property
        def name(self) -> str:
            return self._name

        @property
        @pymodelio.do_not_serialize
        def lowercase_name(self) -> str:
            return self._name.lower()

    instance = TestCaseModel(name='Test Name')

    assert instance.lowercase_name == 'test name'
    assert instance.to_dict() == {'name': 'Test Name'}
