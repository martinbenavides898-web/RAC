from __future__ import annotations

from datetime import date, datetime
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st

from rac_core.db import get_activities, get_context_events, get_profile
from rac_core.metrics import week_bounds
from rac_core.theme import TOKENS, render_status_grid


WEEKDAY_LABELS = ["L", "M", "M", "J", "V", "S", "D"]
MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
WEEKDAYS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _format_duration(total_minutes: float) -> str:
    minutes = max(0, int(round(total_minutes)))
    hours, remaining = divmod(minutes, 60)
    return f"{hours} h {remaining:02d} min" if hours else f"{remaining} min"


def _latest_sleep(events: list[dict], profile: dict) -> float:
    for event in sorted(events, key=lambda item: item.get("event_date", ""), reverse=True):
        if event.get("sleep_hours") is not None:
            return float(event["sleep_hours"])
    availability = profile.get("availability_profile") or {}
    return float(availability.get("sleep_reality_hours", 6.0))


def _max_recent_pain(activities: list[dict], profile: dict) -> int:
    values = [int((profile.get("runner_profile") or {}).get("current_pain", 0))]
    for activity in activities[-3:]:
        values.extend(
            [
                int(activity.get("pain_before") or 0),
                int(activity.get("pain_during") or 0),
                int(activity.get("pain_after") or 0),
            ]
        )
    return max(values or [0])


def _readiness_copy(*, pain: int, has_sick_day: bool) -> tuple[str, str, int, str, str]:
    if has_sick_day:
        return (
            "Hoy conviene priorizar recuperación y observar cómo evolucionan tus síntomas.",
            "RECUPERACIÓN",
            25,
            "Movilidad suave · sin impacto",
            "La prioridad de hoy es recuperarte. No hay una sesión pendiente que debas pagar después.",
        )
    if pain >= 4:
        return (
            "Hoy conviene bajar la carga y revisar las molestias antes de correr.",
            "RECUPERACIÓN",
            25,
            "Movilidad suave · sin impacto",
            "Hay una señal de dolor relevante. RAC no aumentará distancia ni intensidad hasta ver su evolución.",
        )
    return (
        "Hoy estás en condiciones de hacer un rodaje suave.",
        "RODAJE SUAVE",
        40,
        "Ritmo conversacional · Z2",
        "Mantén el esfuerzo controlado. Hoy importa acumular minutos, no buscar velocidad.",
    )


now = datetime.now(ZoneInfo("America/Santiago"))
today = now.date()
start, end = week_bounds(today)

activities = get_activities(start.isoformat(), end.isoformat(), descending=False)
events = get_context_events(start.isoformat(), end.isoformat(), descending=False)
profile = get_profile()

runner = profile.get("runner_profile") or {}
name = str(runner.get("preferred_name") or "Martín")
sleep_hours = _latest_sleep(events, profile)
pain = _max_recent_pain(activities, profile)
has_sick_day = any(
    event.get("event_date") == today.isoformat() and event.get("event_type") == "Sick day"
    for event in events
)

readiness_text, workout_name, workout_minutes, workout_zone, workout_copy = _readiness_copy(
    pain=pain,
    has_sick_day=has_sick_day,
)

if pain == 0:
    legs_value = "Normales"
    discomfort_value = "Ninguna"
    discomfort_color = TOKENS["green"]
    discomfort_progress = 100
elif pain <= 2:
    legs_value = "Algo cargadas"
    discomfort_value = "Leves"
    discomfort_color = TOKENS["cyan"]
    discomfort_progress = 72
else:
    legs_value = "Cargadas"
    discomfort_value = f"{pain}/10"
    discomfort_color = TOKENS["crimson"]
    discomfort_progress = 38

sleep_progress = int(min(100, max(18, sleep_hours / 8 * 100)))
session_count = len(activities)
total_distance = sum(float(item.get("distance_km") or 0) for item in activities)
total_minutes = sum(float(item.get("duration_min") or 0) for item in activities)
trained_weekdays = {
    date.fromisoformat(item["activity_date"]).weekday()
    for item in activities
    if item.get("activity_date")
}

if has_sick_day:
    explanation = (
        "Registraste un Sick Day. La sesión se reemplaza por recuperación y no genera deuda deportiva. "
        "La próxima carga se decidirá según tu evolución."
    )
elif pain >= 4:
    explanation = (
        "RAC detecta una señal de dolor relevante en tus registros recientes. Antes de progresar, "
        "conviene observar si disminuye y si altera tu forma de caminar o correr."
    )
else:
    explanation = (
        "Vienes retomando continuidad y tu recuperación está limitada por el sueño. "
        "La sesión busca sumar volumen sin aumentar innecesariamente la carga de tus piernas."
    )

greeting = "mañanas" if now.hour < 12 else "tardes" if now.hour < 20 else "noches"
header_html = (
    '<section class="rac-home-header">'
    '<div class="rac-wordmark">RAC</div>'
    f'<h1 class="rac-greeting">Buenas {greeting}, {escape(name)}</h1>'
    f'<div class="rac-date">{WEEKDAYS_ES[today.weekday()]} {today.day} de {MONTHS_ES[today.month - 1]}</div>'
    f'<p class="rac-daily-readiness">{escape(readiness_text)}</p>'
    '</section>'
)
st.html(header_html)

render_status_grid(
    [
        {"label": "Sueño", "value": f"{sleep_hours:g} h", "color": TOKENS["cyan"], "progress": sleep_progress},
        {"label": "Piernas", "value": legs_value, "color": TOKENS["orange"], "progress": 68 if pain <= 2 else 38},
        {"label": "Molestias", "value": discomfort_value, "color": discomfort_color, "progress": discomfort_progress},
    ]
)

with st.container(key="rac_workout_section"):
    st.html(
        '<div class="rac-workout-eyebrow">' + escape(workout_name) + '</div>'
        f'<div class="rac-workout-duration">{workout_minutes}<span>min</span></div>'
        '<div class="rac-workout-zone">' + escape(workout_zone) + '</div>'
        '<p class="rac-workout-copy">' + escape(workout_copy) + '</p>'
    )
    if st.button("INICIAR ENTRENAMIENTO", type="primary", use_container_width=True):
        st.switch_page("ui/register_run.py")

with st.container(key="rac_explanation"):
    with st.expander("¿Por qué este entrenamiento?", expanded=True):
        st.write(explanation)

week_days_html = "".join(
    f'<div class="rac-week-day{" is-trained" if idx in trained_weekdays else ""}{" is-today" if idx == today.weekday() else ""}">{label}</div>'
    for idx, label in enumerate(WEEKDAY_LABELS)
)

weekly_html = (
    '<section class="rac-weekly-card">'
    '<div class="rac-weekly-title">Resumen semanal</div>'
    '<div class="rac-weekly-metrics">'
    f'<div><div class="rac-weekly-value">{session_count} de 3</div><div class="rac-weekly-label">sesiones</div></div>'
    f'<div><div class="rac-weekly-value">{total_distance:.1f} km</div><div class="rac-weekly-label">distancia</div></div>'
    f'<div><div class="rac-weekly-value">{escape(_format_duration(total_minutes))}</div><div class="rac-weekly-label">tiempo total</div></div>'
    '</div>'
    f'<div class="rac-week-strip">{week_days_html}</div>'
    '</section>'
)
st.html(weekly_html)
