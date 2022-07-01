from typing import Any


class ModelSerializer:

    @classmethod
    def serialize(cls, value: Any) -> Any:
        if cls._is_model(value):
            return cls._serialize_model(value)
        if isinstance(value, (list, tuple, set)):
            return [cls.serialize(x) for x in value]
        return value

    @classmethod
    def _serialize_model(cls, model: Any) -> dict:
        serialized = {}
        for attr_name in cls._get_model_attrs(model):
            attr_value = getattr(model, attr_name)
            # If it is a function, we ignore it
            if callable(attr_value):
                continue
            serialized[attr_name] = cls.serialize(attr_value)
        return serialized

    @classmethod
    def _get_model_attrs(cls, model: Any) -> dict:
        return [attr_name for attr_name in dir(model) if not attr_name.startswith('_')]

    @classmethod
    def _is_model(cls, attr_value: Any) -> bool:
        return hasattr(attr_value, '_is_pymodelio_model') and getattr(attr_value, '_is_pymodelio_model')()
