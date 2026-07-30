from datetime import date

import pandas as pd
import streamlit as st

from rac_core.db import query
from rac_core.metrics import pace_text, week_bounds, weekly_verdict
from rac_core.ui_helpers import page_header

page_header("Reporte semanal", "La primera versión usa reglas objetivas; luego RAC añadirá interpretación IA.")

period = st.radio("Semana", ["Semana actual", "Semana pasada"], horizontal=True)
start, end = week_bounds(date.today(), previous=period == "Semana pasada")

activities = query(
    """
    SELECT a.*, s.nickname AS shoe_name
    FROM activities a LEFT JOIN shoes s ON s.id = a.shoe_id
    WHERE activity_date BETWEEN ? AND ?
    ORDER BY activity_date, activity_time
    """,
    (start.isoformat(), end.isoformat()),
)
events = query(
    "SELECT * FROM context_events WHERE event_date BETWEEN ? AND ? ORDER BY event_date",
    (start.isoformat(), end.isoformat()),
)

st.subheader(f"{start.strftime('%d-%m-%Y')} al {end.strftime('%d-%m-%Y')}")

total_distance = sum(float(a["distance_km"]) for a in activities)
total_time = sum(float(a["duration_min"]) for a in activities)
longest = max([float(a["distance_km"]) for a in activities] or [0])
max_pain = max(
    [max(int(a["pain_before"]), int(a["pain_during"]), int(a["pain_after"])) for a in activities] or [0]
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Sesiones", len(activities))
c2.metric("Distancia", f"{total_distance:.1f} km")
c3.metric("Tiempo", f"{total_time:.0f} min")
c4.metric("Fondo mayor", f"{longest:.1f} km")
c5.metric("Dolor máximo", f"{max_pain}/10")

verdict, explanation = weekly_verdict(activities, events)
st.markdown(f"### {verdict}")
st.write(explanation)

study_days = sum(1 for e in events if e["event_type"] == "Día de estudio")
sick_days = sum(1 for e in events if e["event_type"] == "Sick day")
rest_days = sum(1 for e in events if e["event_type"] == "Descanso")
if events:
    st.info(
        f"Contexto: {study_days} día(s) de estudio, {sick_days} sick day(s) y {rest_days} descanso(s). "
        "Estos eventos explican la semana; no generan kilómetros pendientes."
    )

if activities:
    table = pd.DataFrame(
        [
            {
                "Fecha": a["activity_date"],
                "Tipo": a["activity_type"],
                "Distancia (km)": a["distance_km"],
                "Ritmo": pace_text(a["distance_km"], a["duration_min"]),
                "RPE": a["rpe"],
                "Dolor durante": a["pain_during"],
                "Zapatillas": a.get("shoe_name") or "—",
            }
            for a in activities
        ]
    )
    st.dataframe(table, hide_index=True, use_container_width=True)

st.subheader("Prioridad siguiente")
if max_pain >= 4:
    st.warning("Revisar el dolor y su evolución. No aumentar distancia ni intensidad todavía.")
elif len(activities) >= 3:
    st.success("Consolidar la frecuencia antes de buscar una semana espectacular.")
elif study_days or sick_days:
    st.info("Retomar la estructura normal sin intentar recuperar de golpe las sesiones omitidas.")
else:
    st.info("La prioridad es sumar continuidad, no perseguir ritmo todavía.")
