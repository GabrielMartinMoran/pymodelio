from typing import Callable

from pymodelio import shared_vars


def do_not_serialize(method: Callable) -> Callable:
    _add_from_qualname(method.__qualname__)
    return method


def _add_from_qualname(qualname: str) -> None:
    split = qualname.split('.')
    module = '.'.join(split[:-1])
    method = split[len(split) - 1]
    if module not in shared_vars.to_do_not_serialize:
        shared_vars.to_do_not_serialize[module] = set()
    shared_vars.to_do_not_serialize[module].add(method)
