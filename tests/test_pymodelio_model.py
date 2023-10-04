from datetime import datetime, date
from typing import Any, Optional, List, Set, Tuple, Dict, Union

import pytest

from pymodelio import PymodelioModel
from pymodelio.attribute import Attr, PymodelioAttr
from pymodelio.constants import UNDEFINED
from pymodelio.decorators.deserializes import deserializes
from pymodelio.decorators.serializes import serializes
from pymodelio.exceptions.model_validation_exception import ModelValidationException
from pymodelio.exceptions.non_initable_attribute_exception import NonInitableAttributeException
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

    with pytest.raises(NonInitableAttributeException) as ex_info:
        Model(non_initable_model_attr='custom value')
    assert ex_info.value.args[0] == 'non_initable_model_attr attribute is not initable for class Model'


def test_model_init_uses_default_factory_value_when_provided_value_is_UNDEFINED():
    class Model(PymodelioModel):
        model_attr: Attr(int, default_factory=lambda: 12345)

    model = Model(model_attr=UNDEFINED)
    assert model.model_attr == 12345


def test_model_calls_when_validating_attr_method_when_performing_attribute_validations():
    class Model(PymodelioModel):
        model_attr: Attr(str)

        @classmethod
        def __when_validating_an_attr__(cls, attr_name: str, attr_value: Any, attr_path: str, parent_path: str,
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
        _attr_1: Attr(str, init_alias='attr_1')
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


def test_to_dict_serializes_non_pymodelio_attributes_exposed_with_property_decorator():
    class TestCaseModel(PymodelioModel):

        def __once_validated__(self) -> None:
            self.attr_1 = 12345
            self._attr_2 = 54321

        @property
        def attr_2(self) -> int:
            return self._attr_2

    instance = TestCaseModel()

    assert instance.to_dict() == {'attr_2': 54321}


def test_repr_includes_non_pymodelio_attributes_exposed_with_property_decorator():
    class TestCaseModel(PymodelioModel):

        def __once_validated__(self) -> None:
            self.attr_1 = 12345
            self._attr_2 = 54321

        @property
        def attr_2(self) -> int:
            return self._attr_2

    instance = TestCaseModel()

    expected = 'TestCaseModel(attr_2=54321)'

    assert str(instance) == expected


def test_repr_formats_date():
    class TestCaseModel(PymodelioModel):
        d: Attr(date)

    instance = TestCaseModel(d=date(2023, 4, 24))

    assert str(instance) == 'TestCaseModel(d=date(2023, 4, 24))'


def test_model_comparison():
    class TestCaseModel(PymodelioModel):
        attr_1: Attr(int)
        _attr_2: Attr(str, init_alias='attr_2')
        __attr_3: Attr(float, init_alias='attr_3')

    assert TestCaseModel(attr_1=1234, attr_2='Some string', attr_3=123.4) == \
           TestCaseModel(attr_1=1234, attr_2='Some string', attr_3=123.4)

    assert TestCaseModel(attr_1=1234, attr_2='Some string', attr_3=123.4) != \
           TestCaseModel(attr_1=1234, attr_2='invalid string', attr_3=123.4)


def test_model_comparison_ignores_attributes_marked_as_not_comparable():
    class TestCaseModel(PymodelioModel):
        attr_1: Attr(int)
        attr_2: Attr(bool, compare=False)
        _attr_3: Attr(str, init_alias='attr_3', compare=False)
        __attr_4: Attr(float, init_alias='attr_4', compare=False)

    assert TestCaseModel(attr_1=1234, attr_2=True, attr_3='Some string', attr_4=123.4) == \
           TestCaseModel(attr_1=1234, attr_2=False, attr_3='Other string', attr_4=432.1)

    assert TestCaseModel(attr_1=1234, attr_2=True, attr_3='Some string', attr_4=123.4) != \
           TestCaseModel(attr_1=4321, attr_2=True, attr_3='Some string', attr_4=123.4)


def test_model_inner_model_class_is_created_correctly_when_parent_model_was_already_instantiated():
    class TestCaseParentModel(PymodelioModel):
        _attr_1: Attr(int, init_alias='attr_1')

    assert not hasattr(TestCaseParentModel, '_TestCaseParentModel__inner_pymodelio_model')

    parent_instance = TestCaseParentModel(attr_1=987)

    assert getattr(TestCaseParentModel, '_TestCaseParentModel__inner_pymodelio_model') is not None
    assert isinstance(parent_instance, TestCaseParentModel)
    assert parent_instance._attr_1 == 987

    class TestCaseChildModel(TestCaseParentModel):
        _attr_2: Attr(int, init_alias='attr_2')

    assert not TestCaseChildModel.__is_pymodelio_inner_model__
    assert TestCaseChildModel.__model_attrs__ == tuple()
    assert TestCaseChildModel.__pymodelio_parent__ is None
    assert TestCaseChildModel.__serializable_attrs__ == list()
    assert TestCaseChildModel.__exposed_attrs__ == dict()
    assert TestCaseChildModel.__protected_attrs__ == set()
    assert TestCaseChildModel.__private_attrs__ == set()
    assert TestCaseChildModel.__deserializers__ == dict()
    assert not hasattr(TestCaseChildModel, '_TestCaseChildModel__inner_pymodelio_model')

    child_instance = TestCaseChildModel(attr_1=123, attr_2=456)

    assert getattr(TestCaseChildModel, '_TestCaseChildModel__inner_pymodelio_model') is not None
    assert getattr(TestCaseParentModel, '_TestCaseParentModel__inner_pymodelio_model') != \
           getattr(TestCaseChildModel, '_TestCaseChildModel__inner_pymodelio_model')

    assert isinstance(child_instance, TestCaseChildModel)
    assert child_instance._attr_1 == 123
    assert child_instance._attr_2 == 456


def test_patch_completes_instance():
    class InnerModel(PymodelioModel):
        a: Attr(Optional[str])
        b: Attr(Optional[int])

    class ModelToPatch(PymodelioModel):
        a: Attr(Optional[int])
        b: Attr(Optional[float])
        c: Attr(Optional[str])
        d: Attr(Optional[List[int]])
        e: Attr(Optional[InnerModel])

    class ReferenceModel(PymodelioModel):
        a: Attr(int)
        b: Attr(float)
        c: Attr(str)
        d: Attr(List[int])
        e: Attr(InnerModel)

    ref_obj = {'a': 6, 'b': 7.2, 'c': 'other_str_value', 'd': [9, 8, 7]}
    model_to_patch = ModelToPatch(a=5, c='str_value')
    model_to_patch.patch(ref_obj, on_value=None)
    assert model_to_patch.a != ref_obj['a']
    assert model_to_patch.b == ref_obj['b']
    assert model_to_patch.c != ref_obj['c']
    assert model_to_patch.d == ref_obj['d']
    assert model_to_patch.e is None

    ref_obj = ReferenceModel(a=1, b=2.5, c='ref_model_str_value', d=[5, 4, 3, 2, 1], e=InnerModel(a='inner_str', b=2))
    model_to_patch = ModelToPatch(c='str_value', d=[1, 2, 3, 4])
    model_to_patch.patch(ref_obj, on_value=None)
    assert model_to_patch.a == ref_obj.a
    assert model_to_patch.b == ref_obj.b
    assert model_to_patch.c != ref_obj.c
    assert model_to_patch.d != ref_obj.d
    assert model_to_patch.e == ref_obj.e

    ref_obj = ReferenceModel(a=1, b=2.5, c='ref_model_str_value', d=[5, 4, 3, 2, 1], e=InnerModel(a='inner_str', b=2))
    model_to_patch = ModelToPatch(c='str_value', d=[1, 2, 3, 4], e=InnerModel())
    model_to_patch.patch(ref_obj, on_value=None)
    assert model_to_patch.a == ref_obj.a
    assert model_to_patch.b == ref_obj.b
    assert model_to_patch.c != ref_obj.c
    assert model_to_patch.d != ref_obj.d
    assert model_to_patch.e.a == ref_obj.e.a
    assert model_to_patch.e.b == ref_obj.e.b


def test_serializes_decorator_serializes_specific_attr():
    class TestCaseModel(PymodelioModel):
        attr: Attr(str)

        @serializes('attr')
        def serializes_attr(self) -> str:
            return self.attr.upper()

    instance = TestCaseModel(attr='attr_value')
    assert instance.attr == 'attr_value'

    serialized = instance.to_dict()
    assert serialized['attr'] == 'ATTR_VALUE'
