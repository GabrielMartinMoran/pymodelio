import time
from dataclasses import dataclass
from typing import Callable, Dict, Any


def profile_function(function: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = function(*args, **kwargs)
        execution_time = time.time() - start
        PymodelioProfiler.track(function.__qualname__, execution_time)
        return result

    return wrapper


@dataclass
class ProfiledFunction:
    function_name: str
    total_calls: int
    total_seconds: float


class PymodelioProfiler:
    _data: Dict[str, ProfiledFunction] = {}

    @classmethod
    def track(cls, function_name: str, execution_time: float) -> None:
        if function_name not in cls._data:
            cls._data[function_name] = ProfiledFunction(
                function_name=function_name,
                total_calls=1,
                total_seconds=execution_time
            )
        else:
            cls._data[function_name].total_calls += 1
            cls._data[function_name].total_seconds += execution_time

    @classmethod
    def log(cls) -> None:
        results = sorted(cls._data.values(), key=lambda x: x.total_seconds, reverse=True)
        print('\n' + ('=' * 200))
        print('Pymodelio profiling results:')
        for result in results:
            print(
                f'- Function: {result.function_name}\n'
                f'    > Total seconds: {result.total_seconds}\n'
                f'    > Total calls: {result.total_calls}'
            )
        print(('=' * 200) + '\n')
