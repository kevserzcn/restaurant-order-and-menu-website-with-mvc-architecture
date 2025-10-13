from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

ISTANBUL_TZ = ZoneInfo('Europe/Istanbul')
UTC_TZ = ZoneInfo('UTC')


def to_local(dt: datetime | None) -> datetime | None:
    """Convert naive/UTC datetime to Europe/Istanbul timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    return dt.astimezone(ISTANBUL_TZ)


def format_local(dt: datetime | None, fmt: str = '%d.%m.%Y %H:%M') -> str:
    """Format datetime in local timezone using given format."""
    local_dt = to_local(dt)
    return local_dt.strftime(fmt) if local_dt else ''
