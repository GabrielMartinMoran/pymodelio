from datetime import datetime
from typing import List, Any, Optional, Tuple

from pymodelio import PymodelioSettings, PymodelioSetting, shared_vars
from pymodelio.attribute import PymodelioAttr
from pymodelio.constants import UNDEFINED
from pymodelio.decorators.pymodelio_cached import pymodelio_cached
from pymodelio.model_serializer import ModelSerializer
from pymodelio.utils import to_datetime


class PymodelioModel:
    __GENERIC_ALIASES = {'_GenericAlias', '_UnionGenericAlias'}
    __ANNOTATIONS_KEY__ = '__annotations__'

    def __init__(self, *args, auto_validate: bool = True, **kwargs) -> None:
        shared_vars.model_globals[self.__class__.__name__] = self.__class__
        self._model_attrs = self.__get_model_attrs()
        if not kwargs.get('from_dict', False):
            self.__constructor__(*args, auto_validate=auto_validate, **kwargs)

    def __constructor__(self, *args, auto_validate: bool = True, **kwargs) -> None:
        self.__before_init__(*args, **kwargs)
        self.__set_attributes(kwargs)
        self.__before_validate__()
        if auto_validate:
            self.validate()
        self.__once_validated__()

    @classmethod
    def _is_pymodelio_model(cls) -> bool:
        return True

    def __set_attributes(self, kwargs: dict) -> None:
        for attr_name in self._model_attrs:
            model_attr = self._model_attrs[attr_name]
            if not self.__is_initable(attr_name, model_attr):
                if self.__get_exposed_attr_name(attr_name) in kwargs:
                    raise NameError('%s attribute is not initable for class %s' % (attr_name, self.__class__.__name__))
                else:
                    attr_value = model_attr.default_factory()
            else:
                exposed_attr_name = self.__get_exposed_attr_name(attr_name)
                attr_value = kwargs.get(exposed_attr_name, model_attr.default_factory())
                if attr_value == UNDEFINED:
                    attr_value = model_attr.default_factory()
            setattr(self, attr_name, attr_value)

    def __before_init__(self, *args, **kwargs) -> None:
        pass

    def __before_validate__(self) -> None:
        pass

    def __once_validated__(self) -> None:
        pass

    @pymodelio_cached
    def __get_annotations(self) -> dict:
        annotations = self.__annotations__ if hasattr(self, self.__ANNOTATIONS_KEY__) else {}
        for parent in self.__class__.__bases__:
            if hasattr(parent, self.__ANNOTATIONS_KEY__):
                annotations = {**annotations, **parent.__annotations__}
        return annotations

    @pymodelio_cached
    def __get_model_attrs(self) -> dict:
        validated_attrs = {}
        annotations = self.__get_annotations()
        for k in annotations:
            v = annotations[k]
            if isinstance(v, PymodelioAttr):
                validated_attrs[k] = v
        return validated_attrs

    @classmethod
    def __generate_private_attr_prefix(cls, cls_type: type) -> str:
        return '_%s__' % cls_type.__name__

    @pymodelio_cached
    def __get_parent_private_attr_prefixes(self) -> List[str]:
        # Iterate all the parents
        prefixes = []
        for cls in self.__class__.__bases__:
            prefixes.append(self.__generate_private_attr_prefix(cls))
        return prefixes

    @pymodelio_cached
    def __get_private_attr_prefixes(self) -> List[str]:
        return ['__', self.__generate_private_attr_prefix(self.__class__)] + self.__get_parent_private_attr_prefixes()

    @pymodelio_cached
    def __get_exposed_attr_name(self, attr_name: str) -> str:
        # Private attributes
        private_attr_prefix = self.__get_private_attr_prefix(attr_name)
        if private_attr_prefix is not None:
            exposed_attr_name = attr_name[len(private_attr_prefix):]
            if exposed_attr_name.endswith('__'):
                exposed_attr_name = exposed_attr_name[:-2]
            return exposed_attr_name
        # Protected attributes
        if self.__is_protected_attr_name(attr_name, private_checked=True):
            exposed_attr_name = attr_name[1:]
            if exposed_attr_name.endswith('_'):
                exposed_attr_name = exposed_attr_name[:-1]
            return exposed_attr_name
        # Public attributes
        return attr_name

    def __is_protected_attr_name(self, attr_name: str, private_checked: bool = False) -> bool:
        if private_checked:
            is_private = False
        else:
            is_private = self.__is_private_attr_name(attr_name)
        return (not is_private) and attr_name.startswith('_')

    def __is_private_attr_name(self, attr_name: str) -> bool:
        return self.__get_private_attr_prefix(attr_name) is not None

    def __get_private_attr_prefix(self, attr_name: str) -> Optional[str]:
        private_attr_prefixes = self.__get_private_attr_prefixes()
        for private_attr_prefix in private_attr_prefixes:
            if attr_name.startswith(private_attr_prefix):
                return private_attr_prefix
        return None

    def __is_initable(self, attr_name: str, model_attr: PymodelioAttr) -> bool:
        if not model_attr.initable:
            return False
        if (not PymodelioSettings.get(PymodelioSetting.INIT_PROTECTED_ATTRS_BY_DEFAULT)) \
                and self.__is_protected_attr_name(attr_name):
            return False
        if (not PymodelioSettings.get(PymodelioSetting.INIT_PRIVATE_ATTRS_BY_DEFAULT)) \
                and self.__is_private_attr_name(attr_name):
            return False
        return True

    def validate(self, path: str = None) -> None:
        """
        It must raise ModelValidationException in case of an invalid attribute
        """
        # model_attrs = self._get_model_attrs()
        for attr_name in self._model_attrs:
            pymodelio_attr = self._model_attrs[attr_name]
            attr_value = getattr(self, attr_name)
            exposed_attr_name = self.__get_exposed_attr_name(attr_name)
            parent_path = path or self.__class__.__name__
            attr_path = '%s.%s' % (parent_path, exposed_attr_name)
            self._when_validating_attr(attr_name, exposed_attr_name, attr_value, attr_path, parent_path,
                                       pymodelio_attr)
            pymodelio_attr.validate(attr_value, path=attr_path)

    def _when_validating_attr(self, internal_attr_name: str, exposed_attr_name: str, attr_value: Any, attr_path: str,
                              parent_path: str, attr: PymodelioAttr) -> None:
        pass

    @classmethod
    def from_dict(cls, data: dict, auto_validate: bool = True) -> Any:
        instance = cls(from_dict=True)
        attrs = {}
        # model_attrs = instance._get_model_attrs()
        for attr_name in instance._model_attrs:
            model_attr = instance._model_attrs[attr_name]
            exposed_attr_name = instance.__get_exposed_attr_name(attr_name)
            if model_attr.initable:
                attrs[exposed_attr_name] = cls.__map_attribute(data, exposed_attr_name, model_attr)
        return cls(**attrs, auto_validate=auto_validate)

    @classmethod
    def __map_attribute(cls, data: dict, exposed_attr_name: str, model_attr: PymodelioAttr) -> Any:  # noqa: C901
        attr_value = data.get(exposed_attr_name, model_attr.default_factory())
        if attr_value == UNDEFINED:
            return model_attr.default_factory()
        # Parse dates
        if model_attr.attr_type == datetime and isinstance(attr_value, str):
            try:
                return to_datetime(attr_value)
            except Exception:
                return attr_value
        if hasattr(model_attr.attr_type, '_is_pymodelio_model') and model_attr.attr_type._is_pymodelio_model() and \
                isinstance(attr_value, dict):
            return model_attr.attr_type.from_dict(attr_value, auto_validate=False)
        if isinstance(attr_value, list):
            if model_attr.attr_type == list or len(model_attr.attr_type.__args__) == 0:
                list_type = None
            else:
                list_type = model_attr.attr_type.__args__[0]
            # If the type of the list is not specified. For instance -> a: List
            if list_type is None:
                return attr_value
            # If the type is more than one. For instance -> a: List[Union[int, float]]
            if list_type.__class__.__name__ in cls.__GENERIC_ALIASES:
                print('WARNING: pymodelio automatic deserialization does not handle multi typed lists of models')
                return attr_value
            # If the type is not a model
            if not hasattr(list_type, '_is_pymodelio_model') or not list_type._is_pymodelio_model():
                return attr_value
            # At this point, the list is a list of models
            return [list_type.from_dict(x, auto_validate=False) for x in attr_value]
        return attr_value

    def to_dict(self) -> dict:
        return ModelSerializer.serialize(self)

    def _get_serializable_attrs(self) -> List[Tuple[str, Any]]:
        attrs = []
        for attr_name in self.__get_serializable_attr_names():
            attr_value = getattr(self, attr_name)
            # If it is a function, we ignore it
            if not callable(attr_value):
                attrs.append((attr_name, attr_value))
        return attrs

    @pymodelio_cached
    def __get_serializable_attr_names(self) -> List[str]:
        return [attr_name for attr_name in dir(self) if
                not attr_name.startswith('_') and not self.__is_marked_as_do_not_serialize(attr_name)]

    def __is_marked_as_do_not_serialize(self, attr_name: str) -> bool:
        class_qualname = self.__class__.__qualname__
        if class_qualname not in shared_vars.to_do_not_serialize:
            return False
        return attr_name in shared_vars.to_do_not_serialize[class_qualname]

    def __repr__(self) -> str:
        formatted_fields = []

        for attr_name, attr_value in self._get_serializable_attrs():
            formatted_attr_value = self.__format_attr_value(attr_value)
            formatted_fields.append('%s=%s' % (attr_name, formatted_attr_value))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(formatted_fields))

    @classmethod
    def __format_attr_value(cls, value: Any) -> Any:
        if isinstance(value, str):
            return "'%s'" % value
        if isinstance(value, PymodelioModel):
            return str(value)
        if isinstance(value, datetime):
            return "datetime(%s, %s, %s, %s, %s, %s, %s, %s)" % (
                value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond,
                value.tzinfo
            )
        return value
