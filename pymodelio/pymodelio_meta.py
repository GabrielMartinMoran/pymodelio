from typing import List, Optional, Tuple, Set, Dict

from pymodelio import shared_vars
from pymodelio.attribute import PymodelioAttr


def _get_annotations(cls: type) -> dict:
    annotations = cls.__annotations__ if hasattr(cls, '__annotations__') else {}
    for parent in cls.__bases__:
        if hasattr(parent, '__annotations__'):
            annotations = {**annotations, **parent.__annotations__}
    return annotations


def _get_model_attrs(cls: type) -> dict:
    validated_attrs = {}
    annotations = _get_annotations(cls)
    for k in annotations:
        v = annotations[k]
        if isinstance(v, PymodelioAttr):
            validated_attrs[k] = v
    return validated_attrs


def _get_serializable_attr_names(cls: type, attr_names: Set[str]) -> List[str]:
    return [
        attr_name for attr_name in attr_names if
        attr_name[0] != '_' and not _is_marked_as_do_not_serialize(cls, attr_name)
    ]


def _is_marked_as_do_not_serialize(cls: type, attr_name: str) -> bool:
    class_qualname = cls.__qualname__
    if class_qualname not in shared_vars.to_do_not_serialize:
        return False
    return attr_name in shared_vars.to_do_not_serialize[class_qualname]


def _generate_private_attr_prefix(cls_type: type) -> str:
    return '_%s__' % cls_type.__name__


def _get_parent_private_attr_prefixes(cls: type) -> List[str]:
    # Iterate all the parents
    return [_generate_private_attr_prefix(cls) for cls in cls.__bases__]


def _get_private_attr_prefixes(pmcls: type) -> List[str]:
    return ['__', _generate_private_attr_prefix(pmcls)] + _get_parent_private_attr_prefixes(pmcls)


def _get_private_attr_prefix(pmcls: type, attr_name: str) -> Optional[str]:
    private_attr_prefixes = _get_private_attr_prefixes(pmcls)
    for private_attr_prefix in private_attr_prefixes:
        if attr_name.startswith(private_attr_prefix):
            return private_attr_prefix
    return None


def _is_private_attr_name(pmcls: type, attr_name: str) -> bool:
    return _get_private_attr_prefix(pmcls, attr_name) is not None


def _is_protected_attr_name(attr_name: str) -> bool:
    return attr_name.startswith('_')


def _get_exposed_attr_name(pmcls: type, attr_name: str, attr: PymodelioAttr) -> Tuple[str]:
    # Private attributes
    if _is_private_attr_name(pmcls, attr_name):
        return tuple()
    # Protected attributes
    if _is_protected_attr_name(attr_name):
        return tuple()
    # Public attributes
    return (attr_name,)


def _generate_exposed_attrs_map(cls: type, attrs: dict) -> Dict[str, Tuple[str]]:
    exposed_attrs = {}
    for attr_name in attrs:
        attr = attrs[attr_name]
        if len(attr.init_aliases) > 0:
            exposed_attrs[attr_name] = attr.init_aliases
        else:
            exposed_attrs[attr_name] = _get_exposed_attr_name(cls, attr_name, attr)
    return exposed_attrs


def _get_custom_deserializers(pmcls: type, cls_dir: List[str]) -> dict:
    return {
        exposed_attr_name: deserializer_function
        for attr_name in cls_dir
        if hasattr((deserializer_function := getattr(pmcls, attr_name)), '__deserializes__')
        for exposed_attr_name in deserializer_function.__deserializes__
    }


def _get_custom_serializers(pmcls: type, cls_dir: List[str]) -> dict:
    serializers = {}
    for attr_name in cls_dir:
        serializer_function = getattr(pmcls, attr_name)
        if hasattr(serializer_function, '__serializes__'):
            serializers[serializer_function.__serializes__] = serializer_function
    return serializers


class PymodelioMeta(type):
    IS_INNER_MODEL_KEY = '__is_pymodelio_inner_model__'

    @classmethod
    def prepare(cls, pmcls: type) -> type:
        model_attrs = _get_model_attrs(pmcls)
        attr_names = tuple(model_attrs.keys())

        protected_attrs = set()
        private_attrs = set()
        for attr_name in attr_names:
            if _is_private_attr_name(pmcls, attr_name):
                private_attrs.add(attr_name)
            elif _is_protected_attr_name(attr_name):
                protected_attrs.add(attr_name)

        cls_dir = dir(pmcls)

        inner_dict = {
            '__slots__': attr_names,
            PymodelioMeta.IS_INNER_MODEL_KEY: True,
            '__pymodelio_parent__': pmcls,
            '__model_attrs__': tuple((k, model_attrs[k]) for k in model_attrs),
            '__serializable_attrs__': _get_serializable_attr_names(pmcls, set(cls_dir + list(attr_names))),
            '__exposed_attrs__': _generate_exposed_attrs_map(pmcls, model_attrs),
            '__protected_attrs__': protected_attrs,
            '__private_attrs__': private_attrs,
            '__deserializers__': _get_custom_deserializers(pmcls, cls_dir),
            '__serializers__': _get_custom_serializers(pmcls, cls_dir)
        }

        inner_class = type(pmcls.__name__, (pmcls,) + pmcls.__bases__, inner_dict)

        pmcls._set_inner_model(inner_class)

        return inner_class

    def __call__(pmcls, *args, **kwargs):
        # If it is an inner model
        if hasattr(pmcls, PymodelioMeta.IS_INNER_MODEL_KEY) and pmcls.__is_pymodelio_inner_model__:
            return super().__call__(*args, **kwargs)

        # If it has an inner model already defined
        inner_model = pmcls._get_inner_model()
        if inner_model is not None:
            return inner_model(*args, **kwargs)

        inner_model = PymodelioMeta.prepare(pmcls)

        shared_vars.model_globals[inner_model.__name__] = inner_model

        return inner_model(*args, **kwargs)
