from copy import deepcopy
from typing import Any

from pymodelio.settings.pymodelio_setting import PymodelioSetting


class PymodelioSettings:
    __initial_settings = {
        PymodelioSetting.AUTO_PARSE_DATES_AS_UTC: False,
        PymodelioSetting.USE_DEFAULT_ATTR_VALIDATOR_IF_NOT_DEFINED: True
    }

    __settings = deepcopy(__initial_settings)

    @classmethod
    def set(cls, setting: PymodelioSetting, value: Any) -> None:
        expected_type = cls.__settings[setting].__class__
        assert isinstance(value, expected_type), f'Value for setting {setting} must be of type {expected_type}'
        cls.__settings[setting] = value

    @classmethod
    def get(cls, setting: PymodelioSetting) -> Any:
        return cls.__settings[setting]

    @classmethod
    def reset(cls) -> None:
        cls.__settings = deepcopy(cls.__initial_settings)
