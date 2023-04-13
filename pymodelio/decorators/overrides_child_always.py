from typing import Callable

from pymodelio import shared_vars


def overrides_child_always(method: Callable) -> Callable:
    shared_vars.base_model_overrides_child_always.append(method)
    return method
