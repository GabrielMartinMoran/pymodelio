from src.attribute import Attribute


class BaseModel:

    def __init__(self, *args, **kwargs) -> None:
        self.__before_init__(*args, **kwargs)
        for attr_name, model_attr in self._get_model_attrs().items():
            if not model_attr.initable:
                if attr_name in kwargs:
                    raise NameError(f'{attr_name} attribute is not initable for class {self.__class__.__name__}')
                continue
            exposed_attr_name = self._get_exposed_attr_name(attr_name)
            attr_value = kwargs.get(exposed_attr_name, model_attr.default_factory())
            setattr(self, attr_name, attr_value)
        self.__before_validate__()
        auto_validate = kwargs.get('auto_validate', True)
        if auto_validate:
            self.validate()
        self.__once_validated__()

    @classmethod
    def __before_init__(cls, *args, **kwargs) -> None:
        pass

    @classmethod
    def __before_validate__(cls) -> None:
        pass

    @classmethod
    def __once_validated__(cls) -> None:
        pass

    def _get_model_attrs(self) -> dict:
        validated_attrs = {}
        annotations = self.__annotations__ if hasattr(self, '__annotations__') else {}
        for k, v in annotations.items():
            if isinstance(v, Attribute):
                validated_attrs[k] = v
            # If Validated is a type and not an instance, it instantiates it using default values default
            elif v.__origin__ == Attribute:
                validated_attrs[k] = v()
        return validated_attrs

    @classmethod
    def _get_exposed_attr_name(cls, attr_name: str) -> str:
        # Protected attributes
        if attr_name.startswith('__'):
            exposed_attr_name = attr_name[2:]
            if exposed_attr_name.endswith('__'):
                exposed_attr_name = exposed_attr_name[:2]
            return exposed_attr_name
        # Private attributes
        if attr_name.startswith('_'):
            exposed_attr_name = attr_name[1:]
            if exposed_attr_name.endswith('_'):
                exposed_attr_name = exposed_attr_name[:1]
            return exposed_attr_name
        # Public attributes
        return attr_name

    def validate(self, path: str = None) -> None:
        """
        It must raise ModelValidationException in case of an invalid attribute
        """
        for attr_name, validator in self._get_model_attrs().items():
            attr_value = getattr(self, attr_name)
            validator.validate(attr_value, path=f'{path or self.__class__.__name__}.{attr_name}')
