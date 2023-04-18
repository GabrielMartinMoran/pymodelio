from datetime import timezone, datetime

import ciso8601

from pymodelio import PymodelioSetting, PymodelioSettings


def default_is_pymodelio_model() -> bool:
    return False


def to_datetime(str_date: str) -> datetime:
    dt = ciso8601.parse_datetime(str_date)
    if PymodelioSettings.get(PymodelioSetting.AUTO_PARSE_DATES_AS_UTC):
        return dt.replace(tzinfo=timezone.utc)
    return dt
