from datetime import datetime
from typing import Any, Optional, List, Set, Tuple, Dict, Union

import pytest

from pymodelio import PymodelioModel, PymodelioSettings, PymodelioSetting
from pymodelio.attribute import Attr, PymodelioAttr
from pymodelio.constants import UNDEFINED
from pymodelio.decorators.deserializes import deserializes
from pymodelio.exceptions.model_validation_exception import ModelValidationException
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
    assert ex_info.value.args[0] == 'Computer._cpu._frequency is not instance of int'


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
    assert ex_info.value.args[0] == 'Computer._disks[1].size is not instance of int'


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


def test_model_initialization_sets_protected_attributes_when_init_by_public_alias_is_true():
    class Model(PymodelioModel):
        _protected_attr_1: Attr(int, init_by_public_alias=True)
        _protected_attr_2_: Attr(str, init_by_public_alias=True)

        @property
        def protected_attr_1(self) -> int:
            return self._protected_attr_1

        @property
        def protected_attr_2(self) -> str:
            return self._protected_attr_2_

    instance_1 = Model(protected_attr_1=12345, protected_attr_2='asd')
    assert instance_1.protected_attr_1 == 12345
    assert instance_1.protected_attr_2 == 'asd'


def test_model_initialization_sets_private_attributes_when_init_by_public_alias_is_true():
    class Model(PymodelioModel):
        __private_attr_1: Attr(int, init_by_public_alias=True)

        @property
        def private_attr_1(self) -> int:
            return self.__private_attr_1

    class ChildModel(Model):
        __private_attr_2: Attr(str, init_by_public_alias=True)
        __private_attr_3__: Attr(float, init_by_public_alias=True)

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
        def _when_validating_attr(cls, attr_name: str, attr_value: Any, attr_path: str, parent_path: str,
                                  attr: PymodelioAttr) -> None:
            if attr_name == 'model_attr' and attr_value != 'Hello world':
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
    PymodelioSettings.set(PymodelioSetting.INIT_PROTECTED_ATTRS_BY_DEFAULT, False)

    class TestCaseModel(PymodelioModel):
        _name: Attr(str, default_factory=lambda: 'Default factory value')
        __id: Attr(str, default_factory=lambda: 'Default id')

    instance = TestCaseModel(name='Initialized value', id='12345')
    assert instance._name == 'Default factory value'

    PymodelioSettings.reset()


def test_private_attributes_are_not_automatically_instantiated_when_settings_prevent_that_behaviour():
    PymodelioSettings.set(PymodelioSetting.INIT_PRIVATE_ATTRS_BY_DEFAULT, False)

    class TestCaseModel(PymodelioModel):
        _name: Attr(str, default_factory=lambda: 'Default factory value')
        __id: Attr(str, default_factory=lambda: 'Default id')

    instance = TestCaseModel(name='Initialized value', id='12345')

    assert instance._TestCaseModel__id == 'Default id'

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


def test_deserializes_decorator_adds_custom_deserialization_logic_to_an_attr():
    class TestCaseModel(PymodelioModel):
        _attr_1: Attr(str, init_by_public_alias=True)
        attr_2: Attr(str, init_alias='$attr_2')
        __attr_3: Attr(str, init_aliases=['_attr_3'])

        @deserializes('attr_1')
        def deserialize_attr_1(self, value: str) -> str:
            return value.lower()

        @deserializes(['$attr_2', '_attr_3'])
        def deserialize_attr_2_and_attr_3(self, value: str) -> str:
            return value.lower()

    instance = TestCaseModel.from_dict({'attr_1': 'TEST', '$attr_2': 'TEST', '_attr_3': 'TEST'})
    assert instance._attr_1 == 'test'
    assert instance.attr_2 == 'test'
    assert instance._TestCaseModel__attr_3 == 'test'


def test_initialize_aliased_attributes_with_one_alias():
    class TestCaseModel(PymodelioModel):
        public_attr: Attr(str, init_alias='public_attr_alias')
        _protected_attr: Attr(str, init_alias='protected_attr_alias')
        __private_attr: Attr(str, init_alias='private_attr_alias')

    instance = TestCaseModel.from_dict(
        {'public_attr_alias': '1', 'protected_attr_alias': '2', 'private_attr_alias': '3'})
    assert instance.public_attr == '1'
    assert instance._protected_attr == '2'
    assert instance._TestCaseModel__private_attr == '3'

    instance = TestCaseModel(public_attr_alias='1', protected_attr_alias='2', private_attr_alias='3')
    assert instance.public_attr == '1'
    assert instance._protected_attr == '2'
    assert instance._TestCaseModel__private_attr == '3'


def test_initialize_aliased_attributes_with_multiple_aliases():
    class TestCaseModel(PymodelioModel):
        public_attr: Attr(str, init_aliases=['public_attr_alias_1', 'public_attr_alias_2'])
        _protected_attr: Attr(str, init_aliases=['protected_attr_alias_1', 'protected_attr_alias_2'])
        __private_attr: Attr(str, init_aliases=['private_attr_alias_1', 'private_attr_alias_2'])

    instance = TestCaseModel.from_dict(
        {'public_attr_alias_1': '1', 'protected_attr_alias_1': '2', 'private_attr_alias_1': '3'})
    assert instance.public_attr == '1'
    assert instance._protected_attr == '2'
    assert instance._TestCaseModel__private_attr == '3'

    instance = TestCaseModel(public_attr_alias_1='1', protected_attr_alias_1='2', private_attr_alias_1='3')
    assert instance.public_attr == '1'
    assert instance._protected_attr == '2'
    assert instance._TestCaseModel__private_attr == '3'

    instance = TestCaseModel.from_dict(
        {'public_attr_alias_2': '1', 'protected_attr_alias_2': '2', 'private_attr_alias_2': '3'})
    assert instance.public_attr == '1'
    assert instance._protected_attr == '2'
    assert instance._TestCaseModel__private_attr == '3'

    instance = TestCaseModel(public_attr_alias_2='1', protected_attr_alias_2='2', private_attr_alias_2='3')
    assert instance.public_attr == '1'
    assert instance._protected_attr == '2'
    assert instance._TestCaseModel__private_attr == '3'
