from datetime import date

import streamlit as st

from rac_core.db import get_activities, get_context_events
from rac_core.metrics import pace_text, week_bounds
from rac_core.ui_helpers import page_header, persistence_status

page_header("Inicio", "Tu estado actual, sin adornos ni métricas por rellenar.")
persistence_status()

start, end = week_bounds(date.today())
activities = get_activities(start.isoformat(), end.isoformat())
events = get_context_events(start.isoformat(), end.isoformat())

sessions = len(activities)
distance = sum(float(a["distance_km"]) for a in activities)
duration = sum(float(a["duration_min"]) for a in activities)
max_pain = max(
    [
        max(int(a["pain_before"]), int(a["pain_during"]), int(a["pain_after"]))
        for a in activities
    ]
    or [0]
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sesiones esta semana", sessions, help="Meta estimada: 3 sesiones")
c2.metric("Distancia", f"{distance:.1f} km")
c3.metric("Tiempo corriendo", f"{duration:.0f} min")
c4.metric("Dolor máximo", f"{max_pain}/10")

st.subheader("Plan semanal base")
plan_cols = st.columns(3)
plan_cols[0].info("**Martes · 16:00**\n\nCinta · máximo 60 min\n\nRodaje cómodo")
plan_cols[1].info("**Miércoles · 16:00**\n\nCinta o natación · máximo 60 min\n\nSesión corta/controlada")
plan_cols[2].info("**Sábado · 08:00**\n\nCalle, parque o maicillo\n\nFondo cómodo")

st.subheader("Último entrenamiento")
latest = get_activities(descending=True, limit=1)
if latest:
    activity = latest[0]
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Fecha", activity["activity_date"])
    a2.metric("Distancia", f'{float(activity["distance_km"]):.2f} km')
    a3.metric("Ritmo", pace_text(activity["distance_km"], activity["duration_min"]).replace(" min/km", ""), help="min/km")
    a4.metric("Esfuerzo", f'{activity["rpe"]}/10')
    st.write(
        f'**Superficie:** {activity["surface"]} · '
        f'**Zapatillas:** {activity.get("shoe_name") or "Sin registrar"} · '
        f'**Dolor durante:** {activity["pain_during"]}/10'
    )
    if activity["notes"]:
        st.info(activity["notes"])
else:
    st.info("Todavía no hay entrenamientos registrados. Usa **Registrar entrenamiento**.")

if events:
    st.subheader("Contexto de esta semana")
    labels = {"Sick day": "🤒", "Día de estudio": "📚", "Descanso": "🛌"}
    for event in events:
        st.write(f'{labels.get(event["event_type"], "•")} **{event["event_date"]} — {event["event_type"]}**')
