from __future__ import annotations

from datetime import date, timedelta
from statistics import mean
from typing import Any


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def summarize_training(activities: list[dict[str, Any]], today: date | None = None) -> dict[str, Any]:
    """Summarize recent training with conservative pain and load flags."""
    today = today or date.today()
    recent28 = []
    recent7 = []
    pain_rows = []
    for activity in activities:
        try:
            day = date.fromisoformat(str(activity.get("activity_date", ""))[:10])
        except ValueError:
            continue
        age = (today - day).days
        if 0 <= age < 28:
            recent28.append(activity)
        if 0 <= age < 7:
            recent7.append(activity)
        if 0 <= age < 14:
            pain_rows.append(activity)
    weekly_km = sum(_num(a.get("distance_km")) for a in recent28) / 4
    last7_km = sum(_num(a.get("distance_km")) for a in recent7)
    longest = max((_num(a.get("distance_km")) for a in recent28), default=0.0)
    max_pain = max((max(int(_num(a.get(k))) for k in ("pain_before", "pain_during", "pain_after")) for a in pain_rows), default=0)
    sessions_7 = len(recent7)
    # This is a simple descriptive ratio, not a validated injury-prediction model.
    ratio = last7_km / max(weekly_km, 1.0)
    return {
        "weekly_km_4w_avg": round(weekly_km, 1),
        "last7_km": round(last7_km, 1),
        "longest_recent_km": round(longest, 1),
        "sessions_last7": sessions_7,
        "max_pain_14d": max_pain,
        "recent_load_ratio": round(ratio, 2),
        "sample_28d": len(recent28),
    }


def build_week_plan(
    activities: list[dict[str, Any]],
    available_days: list[str],
    *,
    today: date | None = None,
    race_date: date | None = None,
    race_goal: str = "Completar sano",
) -> dict[str, Any]:
    """Create a conservative 7-day suggestion from logged load, pain, and availability.

    This is decision support, not a medical assessment or a substitute for a coach.
    """
    today = today or date.today()
    summary = summarize_training(activities, today)
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    available = set(available_days)
    km = summary["weekly_km_4w_avg"]
    longest = summary["longest_recent_km"]
    pain = summary["max_pain_14d"]
    ratio = summary["recent_load_ratio"]
    race_weeks = max(0, (race_date - today).days // 7) if race_date else None

    if summary["sample_28d"] == 0:
        status = "BASE SIN DATOS"
        reason = "Hay pocos o ningún registro reciente. Primero necesitamos una semana representativa antes de fijar volumen."
        target_km = 0
    elif pain >= 4:
        status = "PRIORIZAR RECUPERACIÓN"
        reason = "Se registró dolor de 4/10 o más en los últimos 14 días. No se propone progresión; si persiste, empeora o altera la marcha, pausa el impacto y busca evaluación profesional."
        target_km = min(summary["last7_km"], km) * 0.6
    elif ratio > 1.3:
        status = "CONSOLIDAR CARGA"
        reason = "La semana reciente está bastante por encima de tu promedio de cuatro semanas. Se recomienda consolidar en vez de añadir volumen. El cociente es descriptivo, no un predictor clínico."
        target_km = min(summary["last7_km"], km) * 0.9
    else:
        status = "PROGRESIÓN PRUDENTE"
        reason = "Sin una señal de dolor alto registrada, el plan busca mantener continuidad y ajustar el volumen gradualmente. La ausencia de registros no demuestra ausencia de molestias."
        target_km = km * 1.05 if km else 0

    target_km = round(max(0.0, target_km), 1)
    run_days = [d for d in days if d in available]
    sessions = []
    if pain >= 4:
        for d in days:
            sessions.append({"day": d, "type": "Descanso / movilidad suave", "distance_km": 0, "note": "Sin impacto si hay dolor. Reevalúa síntomas."})
    elif not run_days or target_km <= 0:
        for d in days:
            sessions.append({"day": d, "type": "Recuperación o registro", "distance_km": 0, "note": "Configura días disponibles y registra tus sesiones recientes."})
    else:
        count = min(len(run_days), 4)
        run_days = run_days[:count]
        # Long run is capped against the longest logged run to avoid a sudden jump.
        long_run = min(target_km * 0.38, longest * 1.05) if longest > 0 else 0
        remaining = max(0.0, target_km - long_run)
        easy = remaining / max(1, count - 1) if count > 1 else target_km
        for d in days:
            if d not in run_days:
                sessions.append({"day": d, "type": "Descanso", "distance_km": 0, "note": "Recuperación; no hay sesiones que compensar."})
            else:
                idx = run_days.index(d)
                if idx == count - 1 and count > 1:
                    dist = long_run
                    typ = "Fondo suave"
                    note = "Ritmo conversacional; termina con sensación de poder continuar."
                else:
                    dist = min(easy, longest * 0.65) if longest > 0 else easy
                    typ = "Rodaje fácil Z2"
                    note = "Esfuerzo conversacional. Si el dolor cambia tu zancada, detén la sesión."
                sessions.append({"day": d, "type": typ, "distance_km": round(max(0, dist), 1), "note": note})
    return {
        "generated_for": today.isoformat(),
        "status": status,
        "reason": reason,
        "summary": summary,
        "target_km": target_km,
        "sessions": sessions,
        "race_weeks": race_weeks,
        "race_goal": race_goal,
    }
