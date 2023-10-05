from datetime import datetime, date
from typing import Any


class ModelSerializer:

    @classmethod
    def serialize(cls, value: Any) -> Any:
        if hasattr(value, '__is_pymodelio_model__'):
            return cls._serialize_model(value)
        if isinstance(value, (list, tuple, set)):
            return list(map(cls.serialize, value))
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        return value

    @classmethod
    def _serialize_model(cls, model: Any) -> dict:
        serialized = {}
        for attr_name, attr_value in model._get_serializable_attrs():
            if attr_name in model.__serializers__:
                serialized[attr_name] = model.__serializers__[attr_name](model)
            else:
                serialized[attr_name] = cls.serialize(attr_value)
        return serialized
