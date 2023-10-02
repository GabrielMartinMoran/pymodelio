from datetime import datetime, timezone, date
from typing import List, Union, Tuple
from unittest.mock import patch

from pymodelio import PymodelioModel, Attr, UNDEFINED, PymodelioSettings, PymodelioSetting
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
    PymodelioSettings.set(PymodelioSetting.AUTO_PARSE_DATES_AS_UTC, True)

    class TestCaseModel(PymodelioModel):
        dt: Attr(datetime)

    instance = TestCaseModel.from_dict({'dt': '2023-04-15T10:37:10.567892'})
    try:
        assert instance.dt == datetime(2023, 4, 15, 10, 37, 10, 567892, tzinfo=timezone.utc)
    except Exception as e:
        raise e
    finally:
        PymodelioSettings.reset()


def test_from_dict_deserializes_dates_from_string(*args):
    class TestCaseModel(PymodelioModel):
        attr: Attr(date)

    instance = TestCaseModel.from_dict({'attr': '2023-04-24'})

    assert instance.attr == date(2023, 4, 24)


def test_from_dict_sets_attr_by_factory_default_when_value_is_undefined():
    class TestCaseModel(PymodelioModel):
        attr: Attr(str, default_factory=lambda: 'TEST')

    instance = TestCaseModel.from_dict({'attr': UNDEFINED})
    assert instance.attr == 'TEST'


def test_from_dict_sets_datetime_attr_as_the_serialized_value_when_it_fails_on_parsing_the_datetime():
    class TestCaseModel(PymodelioModel):
        attr: Attr(datetime, validator=None)

    instance = TestCaseModel.from_dict({'attr': 'INVALID_DATE'})
    assert instance.attr == 'INVALID_DATE'


def test_from_dict_does_not_deserialize_list_items_when_list_type_was_not_specified():
    class TestCaseModel(PymodelioModel):
        attr: Attr(list, validator=None)

    instance = TestCaseModel.from_dict({'attr': [1, 'a', 2.5]})
    assert instance.attr == [1, 'a', 2.5]


def test_from_dict_does_not_deserialize_list_items_when_list_is_defined_as_union_of_types():
    class TestCaseModel(PymodelioModel):
        attr: Attr(List[Union[int, float]], validator=None)

    instance = TestCaseModel.from_dict({'attr': [1, 2.5]})
    assert instance.attr == [1, 2.5]


def test_from_dict_does_not_deserialize_list_items_when_items_are_not_a_pymodelio_model():
    class ListItem:
        index: int

    class TestCaseModel(PymodelioModel):
        attr: Attr(List[ListItem], validator=None)

    instance = TestCaseModel.from_dict({'attr': [{'index': 1}]})
    assert instance.attr == [{'index': 1}]


def test_from_dict_deserialize_tuple_with_different_types():
    class InnerModel(PymodelioModel):
        foo: Attr(str)

    class TestCaseModel(PymodelioModel):
        attr: Attr(Tuple[int, float, str, InnerModel], validator=None)

    instance = TestCaseModel.from_dict({'attr': [1, 2.5, 'STR', {'foo': 'bar'}]})
    assert instance.attr == (1, 2.5, 'STR', InnerModel(foo='bar'))
