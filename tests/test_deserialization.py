from datetime import datetime, timezone
from unittest.mock import patch

from pymodelio import PymodelioModel, Attr
from tests.test_models.computer import Computer


@patch('uuid.uuid4', new=lambda: '123e4567-e89b-12d3-a456-426614174000')
def test_from_dict_deserializes_the_model(*args):
    data = {
        'serial_no': '123e4567-e89b-12d3-a456-426614174999',
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
    assert computer.to_dict() == Computer.deserialize_from_dict(data).to_dict()


def test_from_dict_deserializes_datetimes_from_string(*args):
    class TestCaseModel(PymodelioModel):
        dt: Attr(datetime)

    instance = TestCaseModel.from_dict({'dt': '2023-04-15T10:37:10.567892'})
    assert instance.dt == datetime(2023, 4, 15, 10, 37, 10, 567892, tzinfo=timezone.utc)
