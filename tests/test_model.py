from typing import Any

import pytest

import pymodelio
from pymodelio import BaseModel, PymodelioSettings, PymodelioSetting
from pymodelio.attribute import Attribute
from pymodelio.constants import UNDEFINED
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
    assert ex_info.value.args[0] == 'Computer.cpu.frequency is not a valid int'


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
    assert ex_info.value.args[0] == 'Computer.disks[1].size is not a valid int'


def test_can_not_init_non_initable_model_attributes():
    @pymodelio.model
    class Model:
        non_initable_model_attr: Attribute[str](initable=False, default_factory=lambda: 'default value')

    with pytest.raises(NameError) as ex_info:
        Model(non_initable_model_attr='custom value')
    assert ex_info.value.args[0] == 'non_initable_model_attr attribute is not initable for class Model'


def test_model_init_uses_default_factory_value_when_provided_value_is_UNDEFINED():
    @pymodelio.model
    class Model:
        model_attr: Attribute[int](default_factory=lambda: 12345)

    model = Model(model_attr=UNDEFINED)
    assert model.model_attr == 12345


def test_model_initialization_sets_private_attribute():
    @pymodelio.model
    class Model:
        __private_attr_1: Attribute[int]()

        @property
        def private_attr_1(self) -> int:
            return self.__private_attr_1

    @pymodelio.model
    class ChildModel(Model):
        __private_attr_2: Attribute[str]()

        @property
        def private_attr_2(self) -> int:
            return self.__private_attr_2

    instance_1 = ChildModel(private_attr_1=12345, private_attr_2='asd')
    instance_2 = ChildModel(private_attr_1=54321, private_attr_2='dsa')
    assert instance_1.private_attr_1 == 12345
    assert instance_1.private_attr_2 == 'asd'
    assert instance_2.private_attr_1 == 54321
    assert instance_2.private_attr_2 == 'dsa'


def test_model_calls_when_validating_attr_method_when_performing_attribute_validations():
    @pymodelio.model
    class Model:
        model_attr: Attribute[str]()

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
        parent_attr: Attribute[int]()

    class ChildModel(ParentModel):
        child_attr: Attribute[str]()

    model = ChildModel(parent_attr=12345, child_attr='asd')
    assert model.parent_attr == 12345
    assert model.child_attr == 'asd'


def test_auto_instantiate_attribute_when_not_instantiated_manually():
    @pymodelio.model
    class TestCaseModel:
        name: Attribute[str]

    model = TestCaseModel(name='Test')
    assert model.name == 'Test'


def test_protected_attributes_are_not_automatically_instantiated_when_settings_prevent_that_behaviour():
    @pymodelio.model
    class TestCaseModel:
        _name: Attribute[str](default_factory=lambda: 'Default factory value')
        __id: Attribute[str](default_factory=lambda: 'Default id')

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
    @pymodelio.model
    class TestCaseModel:
        _name: Attribute[str](default_factory=lambda: 'Default factory value')
        __id: Attribute[str](default_factory=lambda: 'Default id')

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
