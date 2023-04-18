from datetime import datetime
from typing import Any, Optional, List, Set, Tuple, Dict, Union
from unittest.mock import patch

import pytest

from pymodelio import PymodelioModel, PymodelioSettings, PymodelioSetting, shared_vars
from pymodelio.attribute import Attr, PymodelioAttr
from pymodelio.constants import UNDEFINED
from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.pymodelio_cache import PymodelioCache
from tests.test_models.computer import Computer


def test_valid_model_hierarchy():
    data = {
        'serial_no': 'a0d667a2-66b4-40bd-a4f1-3026f7d0bf09',
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
    assert computer.serial_no == data['serial_no']


def test_invalid_submodel_as_child():
    data = {
        'serial_no': 'a0d667a2-66b4-40bd-a4f1-3026f7d0bf09',
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
        Computer.deserialize_from_dict(data)
    assert ex_info.value.args[0] == 'Computer.cpu.frequency is not instance of int'


def test_invalid_submodel_in_list_as_child():
    data = {
        'serial_no': 'a0d667a2-66b4-40bd-a4f1-3026f7d0bf09',
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
        Computer.deserialize_from_dict(data)
    assert ex_info.value.args[0] == 'Computer.disks[1].size is not instance of int'


def test_can_not_init_non_initable_model_attributes():
    class Model(PymodelioModel):
        non_initable_model_attr: Attr(str, initable=False, default_factory=lambda: 'default value')

    with pytest.raises(NameError) as ex_info:
        Model(non_initable_model_attr='custom value')
    assert ex_info.value.args[0] == 'non_initable_model_attr attribute is not initable for class Model'


def test_model_init_uses_default_factory_value_when_provided_value_is_UNDEFINED():
    class Model(PymodelioModel):
        model_attr: Attr(int, default_factory=lambda: 12345)

    model = Model(model_attr=UNDEFINED)
    assert model.model_attr == 12345


def test_model_initialization_sets_protected_attributes():
    class Model(PymodelioModel):
        _protected_attr_1: Attr(int)
        _protected_attr_2_: Attr(str)

        @property
        def protected_attr_1(self) -> int:
            return self._protected_attr_1

        @property
        def protected_attr_2(self) -> str:
            return self._protected_attr_2_

    instance_1 = Model(protected_attr_1=12345, protected_attr_2='asd')
    assert instance_1.protected_attr_1 == 12345
    assert instance_1.protected_attr_2 == 'asd'


def test_model_initialization_sets_private_attributes():
    class Model(PymodelioModel):
        __private_attr_1: Attr(int)

        @property
        def private_attr_1(self) -> int:
            return self.__private_attr_1

    class ChildModel(Model):
        __private_attr_2: Attr(str)
        __private_attr_3__: Attr(float)

        @property
        def private_attr_2(self) -> str:
            return self.__private_attr_2

        @property
        def private_attr_3(self) -> float:
            return self.__private_attr_3__

    instance_1 = ChildModel(private_attr_1=12345, private_attr_2='asd', private_attr_3=123.4)
    instance_2 = ChildModel(private_attr_1=54321, private_attr_2='dsa', private_attr_3=432.1)
    assert instance_1.private_attr_1 == 12345
    assert instance_1.private_attr_2 == 'asd'
    assert instance_1.private_attr_3 == 123.4
    assert instance_2.private_attr_1 == 54321
    assert instance_2.private_attr_2 == 'dsa'
    assert instance_2.private_attr_3 == 432.1


def test_model_calls_when_validating_attr_method_when_performing_attribute_validations():
    class Model(PymodelioModel):
        model_attr: Attr(str)

        @classmethod
        def _when_validating_attr(cls, internal_attr_name: str, exposed_attr_name: str, attr_value: Any,
                                  attr_path: str, parent_path: str, attr: PymodelioAttr) -> None:
            if exposed_attr_name == 'model_attr' and attr_value != 'Hello world':
                raise ModelValidationException(f'{attr_path} does not match "Hello world"')

    with pytest.raises(ModelValidationException) as ex_info:
        Model(model_attr='custom value')
    assert ex_info.value.args[0] == 'Model.model_attr does not match "Hello world"'


def test_model_definition_using_inheritance_from_base_model():
    class ParentModel(PymodelioModel):
        parent_attr: Attr(int)

    class ChildModel(ParentModel):
        child_attr: Attr(str)

    model = ChildModel(parent_attr=12345, child_attr='asd')
    assert model.parent_attr == 12345
    assert model.child_attr == 'asd'


def test_auto_instantiate_attribute_when_not_instantiated_manually():
    class TestCaseModel(PymodelioModel):
        name: Attr(str)

    model = TestCaseModel(name='Test')
    assert model.name == 'Test'


def test_protected_attributes_are_not_automatically_instantiated_when_settings_prevent_that_behaviour():
    class TestCaseModel(PymodelioModel):
        _name: Attr(str, default_factory=lambda: 'Default factory value')
        __id: Attr(str, default_factory=lambda: 'Default id')

    PymodelioSettings.set(PymodelioSetting.INIT_PROTECTED_ATTRS_BY_DEFAULT, False)

    with pytest.raises(NameError) as ex_info:
        TestCaseModel(name='Initialized value', id='12345')
    try:
        assert ex_info.value.args[0] == '_name attribute is not initable for class TestCaseModel'
    except AssertionError as e:
        raise e
    finally:
        # To always reset the settings
        PymodelioSettings.reset()


def test_private_attributes_are_not_automatically_instantiated_when_settings_prevent_that_behaviour():
    class TestCaseModel(PymodelioModel):
        _name: Attr(str, default_factory=lambda: 'Default factory value')
        __id: Attr(str, default_factory=lambda: 'Default id')

    PymodelioSettings.set(PymodelioSetting.INIT_PRIVATE_ATTRS_BY_DEFAULT, False)

    with pytest.raises(NameError) as ex_info:
        TestCaseModel(name='Initialized value', id='12345')

    try:
        assert ex_info.value.args[0] == '_TestCaseModel__id attribute is not initable for class TestCaseModel'
    except AssertionError as e:
        raise e
    finally:
        # To always reset the settings
        PymodelioSettings.reset()


def test_default_validator_is_used_when_no_validator_is_defined():
    CASES = [
        {
            'type': str,
            'invalid_example': 12345,
            'valid_examples': ["12345"],
        },
        {
            'type': int,
            'invalid_example': "12345",
            'valid_examples': [12345],
        },
        {
            'type': float,
            'invalid_example': "12345",
            'valid_examples': [12345.0],
        },
        {
            'type': dict,
            'invalid_example': "12345",
            'valid_examples': [{'foo': 'bar'}],
        },
        {
            'type': list,
            'invalid_example': "12345",
            'valid_examples': [[1, 2, 3]],
        },
        {
            'type': set,
            'invalid_example': "12345",
            'valid_examples': [{1, 2, 3}],
        },
        {
            'type': tuple,
            'invalid_example': "12345",
            'valid_examples': [(1, 2, 3)],
        },
        {
            'type': bool,
            'invalid_example': "12345",
            'valid_examples': [True],
        },
        {
            'type': datetime,
            'invalid_example': "12345",
            'valid_examples': [datetime.now()],
        },
        {
            'type': Optional[str],
            'invalid_example': 12345,
            'valid_examples': [None, "12345"],
        },
        {
            'type': Optional[dict],
            'invalid_example': 12345,
            'valid_examples': [None, {"foo": "bar"}],
        },
        {
            'type': Optional[List[int]],
            'invalid_example': 12345,
            'valid_examples': [None, [12345]],
        },
        {
            'type': Optional[Set[int]],
            'invalid_example': 12345,
            'valid_examples': [None, {12345}],
        },
        {
            'type': Optional[Tuple[int]],
            'invalid_example': 12345,
            'valid_examples': [None, (12345,)],
        },
        {
            'type': List[int],
            'invalid_example': 12345,
            'valid_examples': [[12345]],
        },
        {
            'type': Set[int],
            'invalid_example': 12345,
            'valid_examples': [{12345}],
        },
        {
            'type': Tuple[int],
            'invalid_example': 12345,
            'valid_examples': [(12345,)],
        },
        {
            'type': Any,
            'invalid_example': None,
            'valid_examples': [12345, "12345", 12345.0, list(), tuple(), set(), dict()],
        },
        {
            'type': Dict,
            'invalid_example': None,
            'valid_examples': [dict()],
        },
        {
            'type': Union[str, int, dict],
            'invalid_example': None,
            'valid_examples': ["12345", 12345, dict()],
        },
        {
            'type': Union[str, int, dict, None],
            'invalid_example': [],
            'valid_examples': ["12345", 12345, dict(), None],
        }
    ]

    for case in CASES:
        _type = case['type']
        invalid_example = case['invalid_example']
        valid_examples = case['valid_examples']

        print(f'Testing type case: {_type}')

        class TestCaseModel(PymodelioModel):
            attr: Attr(_type)

        # Invalid case raises error
        with pytest.raises(ModelValidationException):
            TestCaseModel(attr=invalid_example)

        # Valid cases do not raise error
        for valid_example in valid_examples:
            TestCaseModel(attr=valid_example)

        # Reset the cache because we are re-using the same class
        PymodelioCache.reset()


def test_repr_returns_a_str_representation_of_the_model():
    class Person(PymodelioModel):
        name: Attr(str)
        created_at: Attr(datetime)
        age: Attr(int)
        grandchild: Attr(Optional['Person'])

    person = Person(
        name='Rick Sánchez', created_at=datetime(2023, 4, 18, 17, 33, 15, 605730, None), age=70,
        grandchild=Person(name='Morty Smith', created_at=datetime(2023, 4, 18, 17, 33, 15, 605730, None),
                          age=14)
    )

    expected = ('Person(age=70, created_at=datetime(2023, 4, 18, 17, 33, 15, 605730, None), '
                'grandchild=Person(age=14, created_at=datetime(2023, 4, 18, 17, 33, 15, '
                "605730, None), grandchild=None, name='Morty Smith'), name='Rick Sánchez')")

    assert str(person) == expected


def test_attr_default_value_is_set_when_attr_is_not_initable():
    class TestCaseModel(PymodelioModel):
        attr: Attr(Optional[str], initable=False, default_factory=lambda: 'TEST')

    instance = TestCaseModel()
    assert instance.attr == 'TEST'
