from datetime import datetime, date
from typing import Any, TypeVar

from pymodelio import UNDEFINED
from pymodelio.attribute import PymodelioAttr
from pymodelio.pymodelio_meta import PymodelioMeta
from pymodelio.utils import to_datetime, to_date

T = TypeVar('T')


class ModelDeserializer:
    __GENERIC_ALIASES = {'_GenericAlias', '_UnionGenericAlias'}

    @classmethod
    def deserialize(cls, pmcls: T, data: dict, auto_validate: bool) -> T:
        if pmcls.__inner_pymodelio_model__ is None:
            # Generates the inner class
            PymodelioMeta.prepare(pmcls)
        inner_cls = pmcls.__inner_pymodelio_model__
        attrs = {}
        for attr_name, model_attr in inner_cls.__model_attrs__:
            if model_attr.initable:
                exposed_attr_names = inner_cls.__exposed_attrs__.get(attr_name)
                attr_value = UNDEFINED
                exposed_attr_name_to_use = exposed_attr_names[0]
                for exposed_attr_name in exposed_attr_names:
                    if exposed_attr_name in inner_cls.__deserializers__:
                        if exposed_attr_name in data:
                            exposed_attr_name_to_use = exposed_attr_name
                            attr_value = inner_cls.__deserializers__[exposed_attr_name](
                                data[exposed_attr_name])
                            break
                    else:
                        if exposed_attr_name in data:
                            exposed_attr_name_to_use = exposed_attr_name
                            attr_value = cls.__map_attribute(data, exposed_attr_name, model_attr)
                            break
                if attr_value == UNDEFINED:
                    attrs[exposed_attr_name_to_use] = model_attr.default_factory()
                else:
                    attrs[exposed_attr_name_to_use] = attr_value
        return inner_cls(**attrs, auto_validate=auto_validate)

    @classmethod
    def __map_attribute(cls, data: dict, exposed_attr_name: str, model_attr: PymodelioAttr) -> Any:  # noqa: C901
        attr_value = data[exposed_attr_name]
        # Pymodelio models
        if hasattr(model_attr.attr_type, '__is_pymodelio_model__') and model_attr.attr_type.__is_pymodelio_model__ and \
                isinstance(attr_value, dict):
            return model_attr.attr_type.from_dict(attr_value, auto_validate=False)
        # Lists
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
            if not hasattr(list_type, '__is_pymodelio_model__') or not list_type.__is_pymodelio_model__:
                return attr_value
            # At this point, the list is a list of models
            return [list_type.from_dict(x, auto_validate=False) for x in attr_value]
        # Parse datetimes
        if model_attr.attr_type == datetime and isinstance(attr_value, str):
            try:
                return to_datetime(attr_value)
            except Exception:
                return attr_value
        # Parse dates
        if model_attr.attr_type == date and isinstance(attr_value, str):
            try:
                return to_date(attr_value)
            except Exception:
                return attr_value
        return attr_value
