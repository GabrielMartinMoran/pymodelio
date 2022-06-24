from src.base_model import BaseModel

UNDEFINED = object()


def pymodelio_model(cls: type) -> type:
    """
    Transforms a python class in a pymodelio model.
    Original class constructor is overridden and these methods are allowed to be implemented by the model:

    * def __before_init__(self, *args, **kwargs) -> None
    * def __before_validate__(self) -> None
    * def __once_validated__(self) -> None

    :param cls: Class to be transformed into a pymodelio model
    """
    cls.__init__ = BaseModel.__init__
    if not hasattr(cls, '__before_init__'):
        cls.__before_init__ = BaseModel.__before_init__
    if not hasattr(cls, '__before_validate__'):
        cls.__before_validate__ = BaseModel.__before_validate__
    if not hasattr(cls, '__once_validated__'):
        cls.__once_validated__ = BaseModel.__once_validated__
    cls.validate = BaseModel.validate
    cls._get_model_attrs = BaseModel._get_model_attrs
    cls._get_exposed_attr_name = BaseModel._get_exposed_attr_name
    return cls
