from datetime import timezone, datetime, date

import ciso8601

from pymodelio import PymodelioSetting, PymodelioSettings


def to_date(str_date: str) -> date:
    dt = to_datetime(str_date)
    return dt.date()


def to_datetime(str_datetime: str) -> datetime:
    dt = ciso8601.parse_datetime(str_datetime)
    if PymodelioSettings.get(PymodelioSetting.AUTO_PARSE_DATES_AS_UTC):
        return dt.replace(tzinfo=timezone.utc)
    return dt
