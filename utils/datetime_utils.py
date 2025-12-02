from __future__ import annotations

from datetime import datetime, timezone, timedelta

ISTANBUL_TZ = timezone(timedelta(hours=3))
UTC_TZ = timezone.utc


def to_local(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(ISTANBUL_TZ)


def format_local(dt: datetime | None, fmt: str = '%d.%m.%Y %H:%M') -> str:
    local_dt = to_local(dt)
    return local_dt.strftime(fmt) if local_dt else ''
