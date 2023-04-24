from datetime import datetime, timezone, date

import pymodelio
from pymodelio import Attr, PymodelioModel
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
    class TestCaseModel(PymodelioModel):
        _name: Attr(str, init_alias='name')

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


def test_to_dict_serializes_datetimes_to_iso_strings():
    class TestCaseModel(PymodelioModel):
        dt: Attr(datetime)

    instance = TestCaseModel(dt=datetime(2023, 4, 15, 10, 37, 10, 567892, tzinfo=timezone.utc))
    assert instance.to_dict() == {'dt': '2023-04-15T10:37:10.567892+00:00'}


def test_to_dict_serializes_dates_to_strings():
    class TestCaseModel(PymodelioModel):
        d: Attr(date)

    instance = TestCaseModel(d=date(2023, 4, 24))

    assert instance.to_dict() == {'d': '2023-04-24'}
