from __future__ import annotations

from datetime import datetime, timezone, timedelta

# Istanbul timezone (UTC+3)
ISTANBUL_TZ = timezone(timedelta(hours=3))
UTC_TZ = timezone.utc


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
