from datetime import datetime, date
from typing import List, Any, Tuple, TypeVar, Callable, Dict, Type, Optional, Set, Union

from pymodelio.attribute import PymodelioAttr
from pymodelio.constants import UNDEFINED, PYMODELIO_MODEL_ORIGIN
from pymodelio.exceptions.non_initable_attribute_exception import NonInitableAttributeException
from pymodelio.model_deserializer import ModelDeserializer
from pymodelio.model_serializer import ModelSerializer
from pymodelio.pymodelio_meta import PymodelioMeta

T = TypeVar('T')


class PymodelioModel(metaclass=PymodelioMeta):
    # Only for intellisense
    __is_pymodelio_model__ = True
    __is_pymodelio_inner_model__ = False
    __model_attrs__: Tuple[Tuple[str, PymodelioAttr]] = tuple()
    __pymodelio_parent__ = None
    __serializable_attrs__: List[str] = []
    __exposed_attrs__: Dict[str, Tuple[str]] = {}
    __protected_attrs__: Set[str] = set()
    __private_attrs__: Set[str] = set()
    __deserializers__: Dict[str, Callable] = dict()
    __serializers__: Dict[str, Callable] = dict()
    __origin__ = PYMODELIO_MODEL_ORIGIN

    def __init__(self, /, *, auto_validate: bool = True, **kwargs) -> None:
        kwargs = self.__before_init__(auto_validate=auto_validate, **kwargs)
        self.__set_attributes(kwargs)
        self.__before_validate__()
        if auto_validate:
            self.validate()
        self.__once_validated__()

    def __set_attributes(self, kwargs: dict) -> None:
        for attr_name, model_attr in self.__model_attrs__:
            exposed_attr_names = self.__exposed_attrs__.get(attr_name)
            attr_value = UNDEFINED
            for exposed_attr_name in exposed_attr_names:
                if exposed_attr_name in kwargs:
                    if not model_attr.initable:
                        raise NonInitableAttributeException(
                            '%s attribute is not initable for class %s' % (attr_name, self.__class__.__name__))
                    attr_value = kwargs[exposed_attr_name]
                    break
            if attr_value == UNDEFINED:
                if model_attr.default_factory is not None:
                    attr_value = model_attr.default_factory()
                else:
                    attr_value = None
            setattr(self, attr_name, attr_value)

    def __before_init__(self, **kwargs) -> Dict[str, Any]:
        return kwargs

    def __before_validate__(self) -> None:
        return

    def __once_validated__(self) -> None:
        return

    def validate(self, path: str = None) -> None:
        """
        It must raise ModelValidationException in case of an invalid attribute
        """
        parent_path = path if path is not None else self.__class__.__name__
        for attr_name, model_attr in self.__model_attrs__:
            attr_value = getattr(self, attr_name)
            attr_path = '%s.%s' % (parent_path, attr_name)
            model_attr.validate(attr_value, path=attr_path)
            self.__when_validating_an_attr__(attr_name, attr_value, attr_path, parent_path, model_attr)

    def __when_validating_an_attr__(self, attr_name: str, attr_value: Any, attr_path: str,
                                    parent_path: str, attr: PymodelioAttr) -> None:
        return

    @classmethod
    def from_dict(cls: Type[T], data: dict, auto_validate: bool = True) -> T:
        return ModelDeserializer.deserialize(cls, data, auto_validate)

    def to_dict(self) -> dict:
        return ModelSerializer.serialize(self)

    def _get_serializable_attrs(self) -> List[Tuple[str, Any]]:
        serializable_attrs = self.__serializable_attrs__
        return [
            (attr_name, attr_value)
            for attr_name in serializable_attrs
            if not callable((attr_value := getattr(self, attr_name, None)))
        ]

    def __repr__(self) -> str:
        formatted_fields = []
        for attr_name, attr_value in self._get_serializable_attrs():
            formatted_attr_value = self.__format_attr_value(attr_value)
            formatted_fields.append('%s=%s' % (attr_name, formatted_attr_value))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(sorted(formatted_fields)))

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
        if isinstance(value, date):
            return "date(%s, %s, %s)" % (value.year, value.month, value.day)
        return value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        for attr_name, pymodelio_attr in self.__model_attrs__:
            if pymodelio_attr.compare and getattr(self, attr_name) != getattr(other, attr_name):
                return False
        return True

    @classmethod
    def _get_inner_model(cls) -> Optional[type]:
        return getattr(cls, '_%s__inner_pymodelio_model' % cls.__name__, None)

    @classmethod
    def _set_inner_model(cls, inner_model: type) -> None:
        setattr(cls, '_%s__inner_pymodelio_model' % cls.__name__, inner_model)

    def patch(self, from_: Union[object, dict], on_value: Optional[Any] = None) -> None:
        """
        This method completes the `self` object and the attributes of its inner models  which values match the value
        passed on `on_value` parameter.
        It's recommended to call `validate()` after this method to ensure the attributes are valid.
        :param from_: Object to get the attributes from
        :param on_value: Value to replace on the left
        """
        is_dict = isinstance(from_, dict)
        for attr_name, pm_attr in self.__model_attrs__:
            current_value = getattr(self, attr_name)
            if is_dict:
                reference_value = from_.get(attr_name, on_value)
            else:
                reference_value = getattr(from_, attr_name, on_value)
            if current_value == on_value:
                if reference_value != on_value:
                    setattr(self, attr_name, reference_value)
            elif isinstance(current_value, PymodelioModel):
                current_value.patch(reference_value, on_value=on_value)
