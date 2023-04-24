# Disabling auto validate in children for improving performance
from typing import List

from pymodelio import Attr, PymodelioModel


class ChildModel(PymodelioModel):
    attr: Attr(str)


class ParentModel(PymodelioModel):
    children: Attr(List[ChildModel])


parent_model = ParentModel(
    children=[
        ChildModel(attr='child_1', auto_validate=False),
        ChildModel(attr='child_2', auto_validate=False),
        ChildModel(attr='child_3', auto_validate=False)
    ]
)

print(parent_model)
# > ParentModel(children=[ChildModel(attr='child_1'), ChildModel(attr='child_2'), ChildModel(attr='child_3')])
