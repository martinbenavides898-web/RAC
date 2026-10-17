from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def pace_text(distance_km: float, duration_min: float) -> str:
    if distance_km <= 0:
        return "—"
    pace = duration_min / distance_km
    minutes = int(pace)
    seconds = round((pace - minutes) * 60)
    if seconds == 60:
        minutes += 1
        seconds = 0
    return f"{minutes}:{seconds:02d} min/km"


def week_bounds(reference: date, previous: bool = False) -> tuple[date, date]:
    monday = reference - timedelta(days=reference.weekday())
    if previous:
        monday -= timedelta(days=7)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def weekly_verdict(activities: list[dict[str, Any]], events: list[dict[str, Any]]) -> tuple[str, str]:
    if not activities:
        if events:
            return (
                "Semana interrumpida",
                "No hubo running registrado, pero existen eventos de contexto. La semana no debe tratarse automáticamente como falta de disciplina.",
            )
        return "Semana sin datos", "Todavía no hay registros suficientes para evaluar esta semana."

    max_pain = max(
        max(int(a.get("pain_before") or 0), int(a.get("pain_during") or 0), int(a.get("pain_after") or 0))
        for a in activities
    )
    sessions = len(activities)

    if max_pain >= 4:
        return (
            "Semana con señal de ajuste",
            "Se registró dolor relevante. La prioridad siguiente es revisar su evolución antes de aumentar carga.",
        )
    if sessions >= 3 and max_pain <= 2:
        return (
            "Progreso estable",
            "Se logró una frecuencia sólida sin señales importantes de dolor. Conviene consolidar antes de subir agresivamente.",
        )
    if sessions == 2:
        return (
            "Continuidad parcial",
            "Hubo una base útil de entrenamiento, aunque todavía falta consolidar la frecuencia semanal objetivo.",
        )
    return (
        "Semana de mantenimiento",
        "Una sesión suma, pero todavía no permite concluir que la carga semanal esté consolidada.",
    )
