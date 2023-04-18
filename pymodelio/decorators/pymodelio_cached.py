from typing import Callable

from pymodelio import PymodelioSettings, PymodelioSetting
from pymodelio.pymodelio_cache import PymodelioCache


def pymodelio_cached(function: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        if PymodelioSettings.get(PymodelioSetting.USE_CACHE_OPTIMIZATIONS):
            qualname = args[0].__class__.__qualname__
            # kwargs are not included in the key
            key = '%s%s%s' % (qualname, function.__name__, args[1:])
            if PymodelioCache.has(key):
                return PymodelioCache.get(key)
            result = function(*args, **kwargs)
            PymodelioCache.put(key, result)
            return result
        else:
            return function(*args, **kwargs)

    return wrapper
