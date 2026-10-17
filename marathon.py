from __future__ import annotations

from datetime import date, timedelta
import math
import xml.etree.ElementTree as ET

import pandas as pd
import streamlit as st

from rac_core.db import get_activities, get_profile, set_profile_value
from rac_core.race_calendar import (
    LEGACY_PLACEHOLDER_DATE,
    OFFICIAL_MARATHON_DATE_2027,
    days_until_race,
    parse_iso_date,
    today_santiago,
    training_phases,
)
from rac_core.ui_helpers import page_header

RACE_KEY = "rac_2_marathon"
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
GOALS = ["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Por definir"]


def _gpx_summary(raw: bytes) -> dict:
    root = ET.fromstring(raw)
    points = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "trkpt":
            lat, lon = float(node.attrib["lat"]), float(node.attrib["lon"])
            ele_node = next((x for x in node if x.tag.rsplit("}", 1)[-1] == "ele"), None)
            ele = float(ele_node.text) if ele_node is not None and ele_node.text else None
            points.append((lat, lon, ele))
    if len(points) < 2:
        raise ValueError("El GPX no contiene suficientes puntos de recorrido.")
    distance, gain, loss = 0.0, 0.0, 0.0
    elevations = [p[2] for p in points if p[2] is not None]
    for a, b in zip(points, points[1:]):
        lat1, lon1, ele1 = a
        lat2, lon2, ele2 = b
        dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        h = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        distance += 6371.0 * 2 * math.asin(min(1.0, math.sqrt(h)))
        if ele1 is not None and ele2 is not None:
            delta = ele2 - ele1
            if delta > 0:
                gain += delta
            else:
                loss -= delta
    return {
        "distance_km": round(distance, 2),
        "elevation_gain_m": round(gain),
        "elevation_loss_m": round(loss),
        "min_elevation_m": round(min(elevations)) if elevations else None,
        "max_elevation_m": round(max(elevations)) if elevations else None,
        "track_points": len(points),
    }


page_header(
    "Maratón 42K · RAC 2.0",
    "Centro de preparación con calendario, lectura de carga reciente y análisis inicial de recorridos GPX.",
)

profile = get_profile()
saved = profile.get(RACE_KEY, {})
if not isinstance(saved, dict):
    saved = {}

# Keep an already saved date visible rather than silently overwriting user data.
# The official date is used only when no valid saved date exists.
saved_date_value = saved.get("race_date")
race_date_default = parse_iso_date(saved_date_value, OFFICIAL_MARATHON_DATE_2027)
today = today_santiago()

st.subheader("Tu carrera objetivo")
st.caption("Fecha oficial publicada por la organización: domingo 16 de mayo de 2027.")
st.markdown("Fuente oficial: [Maratón de Santiago · Preguntas frecuentes](https://maratondesantiago.cl/contacto/preguntas-frecuentes/)")

if str(saved_date_value or "").strip() == LEGACY_PLACEHOLDER_DATE.isoformat():
    st.warning(
        "Tu perfil todavía tiene guardado el 18/04/2027, que era la fecha provisional anterior. "
        "No la he sobrescrito automáticamente. Selecciona 16/05/2027 y guarda para actualizarla."
    )

with st.form("rac_marathon_settings"):
    c1, c2 = st.columns(2)
    race_date = c1.date_input(
        "Fecha de la maratón",
        value=race_date_default,
        help="La fecha oficial publicada para 2027 es el 16 de mayo. La fecha se mantiene configurable.",
        format="DD/MM/YYYY",
    )
    saved_goal = saved.get("goal", "Completar sano")
    goal = c2.selectbox(
        "Prioridad",
        GOALS,
        index=GOALS.index(saved_goal) if saved_goal in GOALS else 0,
    )
    saved_days = saved.get("available_days", ["Martes", "Jueves", "Domingo"])
    if not isinstance(saved_days, list):
        saved_days = ["Martes", "Jueves", "Domingo"]
    available_days = st.multiselect(
        "Días posibles para correr",
        DAYS,
        default=[d for d in saved_days if d in DAYS],
    )
    submitted = st.form_submit_button("Guardar objetivo", type="primary")

if submitted:
    if race_date < today:
        st.error("La fecha objetivo no puede estar en el pasado. Revisa la fecha antes de guardar.")
    else:
        set_profile_value(
            RACE_KEY,
            {
                **saved,
                "race_date": race_date.isoformat(),
                "goal": goal,
                "available_days": available_days,
                "race_timezone": "America/Santiago",
                "race_date_source": "official_event_website_checked_2026-10-17",
            },
        )
        st.success("Objetivo guardado en Supabase.")
        st.rerun()

remaining = days_until_race(race_date, today)
weeks_remaining = max(0, math.ceil(remaining / 7))
c1, c2, c3 = st.columns(3)
c1.metric("Cuenta regresiva", f"{remaining} días" if remaining >= 0 else "Fecha pasada")
c2.metric("Semanas disponibles", weeks_remaining)
c3.metric("Prioridad", goal)

if race_date == OFFICIAL_MARATHON_DATE_2027:
    st.success("Fecha objetivo configurada para el 16 de mayo de 2027.")

st.subheader("Calendario de preparación")
phases = training_phases(race_date, today)
if remaining < 0:
    st.warning("La fecha configurada ya pasó. Elige una fecha futura para calcular las fases.")
elif remaining < 7 * 19:
    st.warning(
        "Quedan menos de 19 semanas. Las fases mostradas son solo una vista de calendario; "
        "no implican que sea prudente comprimir la preparación ni aumentar la carga para recuperar tiempo."
    )
for phase in phases:
    st.markdown(
        f"**{phase.name}** · {phase.start_date.strftime('%d/%m/%Y')} – "
        f"{phase.end_date.strftime('%d/%m/%Y')} · {phase.weeks} sem."
    )
    st.caption(phase.description)
st.caption(
    "Estas fases son un calendario orientativo calculado desde la fecha objetivo. "
    "Todavía no generan sesiones ni sustituyen el motor de planificación de RAC."
)

st.divider()
st.subheader("Carga de entrenamiento reciente")
try:
    activities = get_activities(
        start_date=(today - timedelta(days=42)).isoformat(),
        end_date=today.isoformat(),
        descending=False,
    )
except Exception as exc:
    st.error("No se pudieron leer los entrenamientos desde Supabase.")
    st.caption(str(exc))
    activities = []

runs = []
for item in activities:
    try:
        km = float(item.get("distance_km") or 0)
    except (TypeError, ValueError):
        km = 0.0
    if km > 0:
        runs.append({**item, "distance_km": km})

if runs:
    df = pd.DataFrame(runs)
    df["activity_date"] = pd.to_datetime(df["activity_date"], errors="coerce")
    df = df.dropna(subset=["activity_date"])
    df["week"] = df["activity_date"].dt.to_period("W").astype(str)
    last7 = df[df["activity_date"] >= pd.Timestamp(today - timedelta(days=6))]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Km últimos 7 días", f"{last7['distance_km'].sum():.1f}")
    c2.metric("Km últimos 42 días", f"{df['distance_km'].sum():.1f}")
    c3.metric("Fondo más largo", f"{df['distance_km'].max():.1f} km")
    c4.metric("Sesiones · 7 días", len(last7))
    weekly = df.groupby("week", as_index=False)["distance_km"].sum()
    st.bar_chart(weekly.set_index("week"))
    pain_rows = [x for x in runs if max(int(x.get("pain_during") or 0), int(x.get("pain_after") or 0)) >= 4]
    if pain_rows:
        st.warning(
            f"Hay {len(pain_rows)} registro(s) con dolor durante o después ≥4/10. "
            "No aumentes la carga automáticamente; revisa evolución y síntomas."
        )
else:
    st.info("No hay sesiones registradas en los últimos 42 días. Registra entrenamientos para que RAC pueda estimar tu carga.")

st.divider()
st.subheader("Analizar recorrido GPX")
st.write("Sube un archivo GPX para estimar distancia y desnivel. Esta primera versión no guarda el archivo automáticamente.")
upload = st.file_uploader("Archivo .gpx", type=["gpx"], key="rac20_gpx")
if upload is not None:
    try:
        summary = _gpx_summary(upload.getvalue())
        c1, c2, c3 = st.columns(3)
        c1.metric("Distancia", f"{summary['distance_km']:.2f} km")
        c2.metric("Desnivel positivo", f"+{summary['elevation_gain_m']} m")
        c3.metric("Desnivel negativo", f"−{summary['elevation_loss_m']} m")
        if summary["min_elevation_m"] is not None:
            st.caption(f"Altitud: {summary['min_elevation_m']}–{summary['max_elevation_m']} m · {summary['track_points']} puntos.")
    except Exception as exc:
        st.error("No pude interpretar el GPX. Comprueba que incluya puntos de track con coordenadas válidas.")
        st.caption(str(exc))

st.divider()
st.subheader("Reglas de seguridad")
st.markdown(
    "- No aumentes la carga solo porque lo diga el calendario.\n"
    "- Si el dolor cambia tu técnica, empeora o persiste, detén la sesión y busca evaluación apropiada.\n"
    "- Esta es la primera pantalla de RAC 2.0; todavía no sustituye un plan individualizado ni una valoración clínica."
)
