from src.validated import Validated


class BaseModel:

    def __init__(self, **kwargs) -> None:
        print(self.__annotations__)
        for attr_name, validator in self._get_validated_attrs().items():
            if not validator.initable:
                continue
            exposed_attr_name = self._get_exposed_attr_name(attr_name)
            attr_value = kwargs.get(exposed_attr_name, validator.default_factory())
            setattr(self, attr_name, attr_value)
        self.validate(True)

    def _get_validated_attrs(self) -> dict:
        validated_attrs = {}
        for k, v in self.__annotations__.items():
            if isinstance(v, Validated):
                validated_attrs[k] = v
            # If Validated is a type and not an instance, it instantiates it using default values default
            elif v.__origin__ == Validated:
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

    def validate(self, check_auto_validate: bool = False, path: str = None) -> None:
        """
        It must raise ModelValidationException in case of an invalid attribute
        """
        for attr_name, validator in self._get_validated_attrs().items():
            if check_auto_validate and not validator.auto_validate:
                continue
            attr_value = getattr(self, attr_name)
            validator.validate(attr_value, path=f'{path or self.__class__.__name__}.{attr_name}')
