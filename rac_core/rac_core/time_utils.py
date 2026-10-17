from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

SANTIAGO_TZ = ZoneInfo("America/Santiago")


def now_cl() -> datetime:
    """Retorna la fecha y hora actual en Santiago de Chile."""
    return datetime.now(SANTIAGO_TZ)


def today_cl() -> date:
    """Retorna la fecha actual en Santiago de Chile."""
    return now_cl().date()
