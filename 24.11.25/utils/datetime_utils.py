"""
Tarih ve Saat Yardımcı Fonksiyonları
====================================
UTC ve İstanbul saat dilimi dönüşümleri için yardımcı fonksiyonlar.

Sabitler:
- ISTANBUL_TZ: İstanbul saat dilimi (UTC+3)
- UTC_TZ: UTC saat dilimi

Fonksiyonlar:
- to_local(dt): UTC/naive datetime'ı İstanbul saat dilimine çevir
- format_local(dt, fmt): Datetime'ı İstanbul saat diliminde formatla

Kullanım:
    # UTC'den İstanbul'a
    local_time = to_local(utc_datetime)
    
    # Formatlı string
    formatted = format_local(datetime.utcnow(), '%d.%m.%Y %H:%M')
    # Çıktı: "19.11.2025 14:30"

Jinja2 Filter:
    {{ order.created_at|datetime_tr }}
    {{ order.created_at|datetime_tr('%d/%m/%Y') }}

Not: Veritabanında UTC, gösterimde İstanbul saat dilimi kullanılır.
"""

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
