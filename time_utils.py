from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

SANTIAGO_TZ = ZoneInfo("America/Santiago")


def now_cl() -> datetime:
    """Current date and time in Santiago, Chile."""
    return datetime.now(SANTIAGO_TZ)


def today_cl() -> date:
    """Current date in Santiago, Chile."""
    return now_cl().date()
