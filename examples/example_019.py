#  Implementing a custom model's serializer
from pymodelio import Attr, PymodelioModel


class CustomModel(PymodelioModel):
    attr: Attr(float)

    def to_dict(self) -> dict:
        return {
            'attr': str(self.attr)
        }


instance = CustomModel(attr=1.0)

serialized = instance.to_dict()

print(serialized)
# {'attr': '1.0'}
