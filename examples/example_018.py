# Implementing a custom model's deserializer
from pymodelio import Attr, PymodelioModel


class CustomModel(PymodelioModel):
    attr: Attr(float)

    @classmethod
    def from_dict(cls, data: dict, auto_validate: bool = True) -> 'CustomModel':
        _attr = data.get('attr', 0.0)
        try:
            _attr = float(_attr)
        except ValueError:
            _attr = 0.0
        return CustomModel(attr=_attr, auto_validate=auto_validate)


instance = CustomModel.from_dict({'attr': '1'})
print(instance)
# > CustomModel(attr=1.0)

instance = CustomModel.from_dict({'attr': 1})
print(instance)
# > CustomModel(attr=1.0)

instance = CustomModel.from_dict({'attr': 'INVALID_FLOAT_VALUE'})
print(instance)
# > CustomModel(attr=0.0)

instance = CustomModel.from_dict({})
print(instance)
# > CustomModel(attr=0.0)
