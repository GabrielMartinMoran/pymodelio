from typing import TypeVar

from pymodelio import shared_vars

T = TypeVar('T')


def model(cls: T) -> T:
    """
    Transforms a python class in a pymodelio model.
    Original class constructor is overridden and these methods are allowed to be implemented by the model:

    * def __before_init__(self, *args, **kwargs) -> None
    * def __before_validate__(self) -> None
    * def __once_validated__(self) -> None
    * def _when_validating_attr(self, internal_attr_name: str, exposed_attr_name: str, attr_value: Any, attr_path: str,
                              parent_path: str, pymodel_attribute: Attribute) -> None
    * to_dict(self) -> dict:

    :param cls: Class to be transformed into a pymodelio model
    """
    for method in shared_vars.base_model_overrides_child_always:
        if isinstance(method, classmethod):
            method_name = method.__func__.__name__
        else:
            method_name = method.__name__
        setattr(cls, method_name, method)
    for method in shared_vars.base_model_overrides_child_if_not_implemented:
        if isinstance(method, classmethod):
            method_name = method.__func__.__name__
        else:
            method_name = method.__name__
        if not hasattr(cls, method_name):
            setattr(cls, method_name, method)

    return cls
