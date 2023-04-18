from typing import Any


class PymodelioCache:
    __cache = {}

    @classmethod
    def put(cls, key: str, value: Any) -> None:
        cls.__cache[key] = value

    @classmethod
    def get(cls, key: str) -> None:
        return cls.__cache[key]

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls.__cache

    @classmethod
    def reset(cls) -> None:
        cls.__cache = {}
