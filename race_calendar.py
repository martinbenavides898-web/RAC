"""Calendar helpers for RAC's marathon target. No Streamlit/Supabase dependency."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

SANTIAGO_TZ = ZoneInfo("America/Santiago")
OFFICIAL_MARATHON_DATE_2027 = date(2027, 5, 16)
LEGACY_PLACEHOLDER_DATE = date(2027, 4, 18)


@dataclass(frozen=True)
class TrainingPhase:
    name: str
    start_date: date
    end_date: date
    weeks: int
    description: str


def today_santiago() -> date:
    """Return today's date in Chile's America/Santiago timezone."""
    return datetime.now(SANTIAGO_TZ).date()


def parse_iso_date(value: object, fallback: date = OFFICIAL_MARATHON_DATE_2027) -> date:
    """Parse an ISO date without crashing on missing or malformed profile data."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return fallback


def days_until_race(race_date: date, today: date | None = None) -> int:
    """Signed number of calendar days until race day, using Santiago's date by default."""
    reference = today if today is not None else today_santiago()
    return (race_date - reference).days


def _phase_lengths(weeks_remaining: int) -> tuple[int, int, int, int]:
    """Return (general/base, specific, taper, extra_base) weeks.

    Preferred template is 9 weeks base + 18 specific + 3 taper. If there is more
    time, the extra becomes base. If less time is available, phases are shortened
    conservatively for display only; this does not generate training sessions.
    """
    if weeks_remaining <= 0:
        return (0, 0, 0, 0)
    taper = min(3, weeks_remaining)
    remaining = weeks_remaining - taper
    specific = min(18, max(0, remaining - min(9, remaining)))
    # Prefer 16-18 specific weeks when possible, without creating negative phases.
    if remaining >= 25:
        specific = 18
    elif remaining >= 19:
        specific = min(18, max(16, remaining - 9))
    else:
        specific = max(0, remaining - min(8, remaining))
    base = max(0, remaining - specific)
    extra_base = max(0, base - 10)
    return base, specific, taper, extra_base


def training_phases(race_date: date, today: date | None = None) -> list[TrainingPhase]:
    """Create a calendar overview ending on race day; does not prescribe workouts."""
    reference = today if today is not None else today_santiago()
    days_remaining = (race_date - reference).days
    if days_remaining <= 0:
        return [TrainingPhase(
            "Carrera / fecha alcanzada", race_date, race_date, 0,
            "La fecha objetivo es hoy o ya pasó; revisa la configuración.",
        )]

    # The visible calendar includes today and race day. Phase lengths are anchored
    # backward from race day so their date ranges are contiguous and end exactly
    # on the selected target date.
    total_weeks = (days_remaining + 6) // 7
    base_weeks, specific_weeks, taper_weeks, _ = _phase_lengths(total_weeks)
    taper_days = min(days_remaining + 1, taper_weeks * 7)
    taper_start = race_date - timedelta(days=taper_days - 1)
    specific_days = min(max(0, days_remaining + 1 - taper_days), specific_weeks * 7)
    specific_start = taper_start - timedelta(days=specific_days) if specific_days else taper_start
    base_start = reference
    phases: list[TrainingPhase] = []

    if specific_days > 0:
        base_end = specific_start - timedelta(days=1)
    else:
        base_end = race_date

    if base_start <= base_end:
        actual_base_weeks = ((base_end - base_start).days + 1 + 6) // 7
        phases.append(TrainingPhase(
            "Base / consolidación", base_start, base_end, actual_base_weeks,
            "Consolidar continuidad y tolerancia a la carga. No implica aumentar kilómetros automáticamente.",
        ))
    if specific_days > 0:
        actual_specific_weeks = (specific_days + 6) // 7
        phases.append(TrainingPhase(
            "Bloque específico", specific_start, taper_start - timedelta(days=1), actual_specific_weeks,
            "Desarrollo específico para la maratón, condicionado al historial y a la recuperación.",
        ))
    if taper_days > 0:
        actual_taper_weeks = (taper_days + 6) // 7
        phases.append(TrainingPhase(
            "Taper / descarga final", taper_start, race_date, actual_taper_weeks,
            "Reducir fatiga y llegar recuperado; la carga concreta se definirá en una etapa posterior.",
        ))
    return phases
