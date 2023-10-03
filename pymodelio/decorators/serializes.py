from typing import Callable


def serializes(name: str) -> Callable:
    def wrapper(func: Callable) -> Callable:
        func.__serializes__ = name
        return func

    return wrapper
