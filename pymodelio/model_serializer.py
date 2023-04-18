from datetime import datetime
from typing import Any


class ModelSerializer:

    @classmethod
    def serialize(cls, value: Any) -> Any:
        if cls._is_model(value):
            return cls._serialize_model(value)
        if isinstance(value, (list, tuple, set)):
            return [cls.serialize(x) for x in value]
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    @classmethod
    def _serialize_model(cls, model: Any) -> dict:
        serialized = {}
        for attr_name, attr_value in model._get_serializable_attrs():
            serialized[attr_name] = cls.serialize(attr_value)
        return serialized

    @classmethod
    def _is_model(cls, attr_value: Any) -> bool:
        return hasattr(attr_value, '_is_pymodelio_model') and getattr(attr_value, '_is_pymodelio_model')()
