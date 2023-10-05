from datetime import datetime, date
from typing import Any, TypeVar, Type

from pymodelio import UNDEFINED
from pymodelio.attribute import PymodelioAttr
from pymodelio.constants import PYMODELIO_MODEL_ORIGIN
from pymodelio.pymodelio_meta import PymodelioMeta
from pymodelio.utils import to_datetime, to_date

T = TypeVar('T')


class ModelDeserializer:
    __GENERIC_ALIASES = ('_GenericAlias', '_UnionGenericAlias')

    @classmethod
    def deserialize(cls, pmcls: Type[T], data: dict, auto_validate: bool) -> T:
        if (inner_cls := pmcls._get_inner_model()) is None:
            # Generates the inner class
            PymodelioMeta.prepare(pmcls)
            inner_cls = pmcls._get_inner_model()
        attrs = {}
        for attr_name, model_attr in inner_cls.__model_attrs__:
            if not model_attr.initable:
                continue
            exposed_attr_names = inner_cls.__exposed_attrs__[attr_name]
            attr_value = UNDEFINED
            exposed_attr_name_to_use = exposed_attr_names[0]
            for exposed_attr_name in exposed_attr_names:
                if exposed_attr_name not in data:
                    continue
                if exposed_attr_name in inner_cls.__deserializers__:
                    exposed_attr_name_to_use = exposed_attr_name
                    attr_value = inner_cls.__deserializers__[exposed_attr_name](data[exposed_attr_name])
                    break
                else:
                    exposed_attr_name_to_use = exposed_attr_name
                    attr_value = cls.__map_attribute(data, exposed_attr_name, model_attr)
                    break
            if attr_value != UNDEFINED:
                attrs[exposed_attr_name_to_use] = attr_value
                continue
            if model_attr.default_factory is not None:
                attrs[exposed_attr_name_to_use] = model_attr.default_factory()
                continue
            else:
                attrs[exposed_attr_name_to_use] = None

        return inner_cls(**attrs, auto_validate=auto_validate)

    @classmethod
    def __map_attribute(cls, data: dict, exposed_attr_name: str, model_attr: PymodelioAttr) -> Any:
        return cls.__deserialize_value(data[exposed_attr_name], model_attr.attr_type, model_attr.attr_type_origin)

    @classmethod
    def __deserialize_value(cls, value: Any, expected_type: Type, expected_type_origin: Any) -> Any:
        if expected_type_origin == PYMODELIO_MODEL_ORIGIN:
            return expected_type.from_dict(value, auto_validate=False)
        if expected_type_origin == list:
            return cls.__deserialize_list(value, expected_type, expected_type_origin)
        if expected_type_origin == tuple:
            return cls.__deserialize_tuple(value, expected_type, expected_type_origin)
        try:
            # Parse datetimes
            if expected_type == datetime and isinstance(value, str):
                return to_datetime(value)
            # Parse dates
            if expected_type == date and isinstance(value, str):
                return to_date(value)
        except Exception:
            return value
        return value

    @classmethod
    def __deserialize_list(cls, attr_value: Any, expected_type: Type, expected_type_origin: Any) -> list:
        if expected_type == expected_type_origin or len(expected_type.__args__) == 0:
            list_type = None
        else:
            list_type = expected_type.__args__[0]
        if list_type is None:
            return attr_value
        # If the type is not a model
        if not getattr(list_type, '__is_pymodelio_model__', False):
            return attr_value
        # If the type is more than one. For instance -> a: List[Union[int, float]]
        if list_type.__class__.__name__ in cls.__GENERIC_ALIASES:
            print('WARNING: pymodelio automatic deserialization does not handle multi typed lists of models')
            return attr_value
        # At this point, the list is a list of models
        return [list_type.from_dict(x, auto_validate=False) for x in attr_value]

    @classmethod
    def __deserialize_tuple(cls, attr_value: Any, expected_type: Type, expected_type_origin: Any) -> tuple:
        if len(attr_value) == 0 or len(attr_value) != len(getattr(expected_type, '__args__', [])):
            # The length of the tuple must match the length of the type
            return tuple(attr_value)
        return tuple(
            cls.__deserialize_value(i_value, i_type, getattr(i_type, '__origin__', i_type)) for i_value, i_type in
            zip(attr_value, expected_type.__args__)
        )
