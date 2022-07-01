from typing import List, Any, _UnionGenericAlias

from pymodelio.attribute import Attribute
from pymodelio.constants import UNDEFINED
from pymodelio.model import overrides_child_always, overrides_child_if_not_implemented
from pymodelio.model_serializer import ModelSerializer


class BaseModel:

    @overrides_child_always
    def __init__(self, *args, auto_validate: bool = True, **kwargs) -> None:
        if not kwargs.get('from_dict', False):
            self.__constructor__(*args, auto_validate=auto_validate, **kwargs)

    @overrides_child_always
    def __constructor__(self, *args, auto_validate: bool = True, **kwargs) -> None:
        self.__before_init__(*args, **kwargs)
        self._set_attributes(kwargs)
        self.__before_validate__()
        if auto_validate:
            self.validate()
        self.__once_validated__()

    @overrides_child_always
    @classmethod
    def _is_pymodelio_model(cls) -> bool:
        return True

    @overrides_child_always
    def _set_attributes(self, kwargs: dict) -> None:
        for attr_name, model_attr in self._get_model_attrs().items():
            if not model_attr.initable:
                if attr_name in kwargs:
                    raise NameError(f'{attr_name} attribute is not initable for class {self.__class__.__name__}')
                continue
            exposed_attr_name = self._get_exposed_attr_name(attr_name)
            attr_value = kwargs.get(exposed_attr_name, model_attr.default_factory())
            if attr_value == UNDEFINED:
                attr_value = model_attr.default_factory()
            setattr(self, attr_name, attr_value)

    @classmethod
    @overrides_child_if_not_implemented
    def __before_init__(cls, *args, **kwargs) -> None:
        pass

    @classmethod
    @overrides_child_if_not_implemented
    def __before_validate__(cls) -> None:
        pass

    @classmethod
    @overrides_child_if_not_implemented
    def __once_validated__(cls) -> None:
        pass

    @overrides_child_always
    def _get_annotations(self) -> dict:
        annotations = self.__annotations__ if hasattr(self, '__annotations__') else {}
        for parent in self.__class__.__bases__:
            if hasattr(parent, '__annotations__'):
                annotations = {**annotations, **parent.__annotations__}
        return annotations

    @overrides_child_always
    def _get_model_attrs(self) -> dict:
        validated_attrs = {}
        annotations = self._get_annotations()
        for k, v in annotations.items():
            if isinstance(v, Attribute):
                validated_attrs[k] = v
            # If Validated is a type and not an instance, it instantiates it using default values default
            elif v.__origin__ == Attribute:
                validated_attrs[k] = v()
        return validated_attrs

    @overrides_child_always
    def _generate_private_attr_prefix(self, cls: type) -> str:
        return f'_{cls.__name__}__'

    @overrides_child_always
    def _get_parent_private_attr_prefixes(self) -> List[str]:
        # Iterate all the parents
        prefixes = []
        for cls in self.__class__.__bases__:
            prefixes.append(self._generate_private_attr_prefix(cls))
        return prefixes

    @overrides_child_always
    def _get_exposed_attr_name(self, attr_name: str) -> str:
        # Private attributes
        private_attr_prefixes = [self._generate_private_attr_prefix(
            self.__class__)] + self._get_parent_private_attr_prefixes()
        for private_attr_prefix in private_attr_prefixes:
            if attr_name.startswith(private_attr_prefix):
                exposed_attr_name = attr_name[len(private_attr_prefix):]
                if exposed_attr_name.endswith('__'):
                    exposed_attr_name = exposed_attr_name[:2]
                return exposed_attr_name
        # Protected attributes
        if attr_name.startswith('_'):
            exposed_attr_name = attr_name[1:]
            if exposed_attr_name.endswith('_'):
                exposed_attr_name = exposed_attr_name[:1]
            return exposed_attr_name
        # Public attributes
        return attr_name

    @overrides_child_always
    def validate(self, path: str = None) -> None:
        """
        It must raise ModelValidationException in case of an invalid attribute
        """
        for attr_name, pymodel_attribute in self._get_model_attrs().items():
            attr_value = getattr(self, attr_name)
            exposed_attr_name = self._get_exposed_attr_name(attr_name)
            parent_path = path or self.__class__.__name__
            attr_path = f'{parent_path}.{exposed_attr_name}'
            self._when_validating_attr(attr_name, exposed_attr_name, attr_value, attr_path, parent_path,
                                       pymodel_attribute)
            pymodel_attribute.validate(attr_value, path=attr_path)

    @overrides_child_if_not_implemented
    def _when_validating_attr(self, internal_attr_name: str, exposed_attr_name: str, attr_value: Any, attr_path: str,
                              parent_path: str, pymodel_attribute: Attribute) -> None:
        pass

    @overrides_child_if_not_implemented
    @classmethod
    def from_dict(cls, data: dict, auto_validate: bool = True) -> Any:
        instance = cls(from_dict=True)
        attrs = {}
        for attr_name, model_attr in instance._get_model_attrs().items():
            exposed_attr_name = instance._get_exposed_attr_name(attr_name)
            if model_attr.initable:
                attrs[exposed_attr_name] = cls._map_attribute(data, exposed_attr_name, model_attr)
        return cls(**attrs, auto_validate=auto_validate)

    @overrides_child_always
    @classmethod
    def _map_attribute(cls, data: dict, exposed_attr_name: str, model_attr: Attribute) -> Any:
        attr_value = data.get(exposed_attr_name, model_attr.default_factory())
        if attr_value == UNDEFINED:
            return model_attr.default_factory()
        if isinstance(attr_value, dict) and (
                hasattr(model_attr.attr_type, '_is_pymodelio_model') and model_attr.attr_type._is_pymodelio_model()
        ):
            return model_attr.attr_type.from_dict(attr_value, auto_validate=False)
        if isinstance(attr_value, list):
            list_type = model_attr.attr_type.__args__[0] if len(model_attr.attr_type.__args__) > 0 else None
            # If the type of the list is not specified. For instance -> a: List
            if list_type is None:
                return attr_value
            # If the type is more than one. For instance -> a: List[Union[int, float]]
            if list_type.__class__ == _UnionGenericAlias:
                print('WARNING: pymodelio automatic deserialization does not handle multi typed lists of models')
                return attr_value
            # If the type is not a model
            if not hasattr(list_type, '_is_pymodelio_model') and not list_type._is_pymodelio_model():
                return attr_value
            # At this point, the list is a list of models
            return [list_type.from_dict(x, auto_validate=False) for x in attr_value]
        return attr_value

    @overrides_child_if_not_implemented
    def to_dict(self) -> dict:
        return ModelSerializer.serialize(self)
