from typing import Callable

from pymodelio import shared_vars


def overrides_child_if_not_implemented(method: Callable) -> Callable:
    shared_vars.base_model_overrides_child_if_not_implemented.append(method)
    return method
