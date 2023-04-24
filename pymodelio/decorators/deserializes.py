from typing import Callable, Iterable, Union


def deserializes(exposed_names: Union[str, Iterable[str]]) -> Callable:
    def wrapper(func: Callable) -> Callable:
        func.__deserializes__ = (exposed_names,) if isinstance(exposed_names, str) else exposed_names
        return classmethod(func)

    return wrapper
