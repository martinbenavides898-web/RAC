from __future__ import annotations

from datetime import date, timedelta
import math
import xml.etree.ElementTree as ET

import pandas as pd
import streamlit as st

from rac_core.db import get_activities, get_profile, set_profile_value
from rac_core.ui_helpers import page_header

RACE_KEY = "rac_2_marathon"
DEFAULT_RACE_DATE = date(2027, 4, 18)  # Editable placeholder, not an official-date claim.
DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def _as_date(value, fallback: date) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return fallback


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
    "Centro de preparación con cuenta regresiva, lectura de carga reciente y análisis inicial de recorridos GPX.",
)

profile = get_profile()
saved = profile.get(RACE_KEY, {})
if not isinstance(saved, dict):
    saved = {}

st.subheader("Tu carrera objetivo")
with st.form("rac_marathon_settings"):
    c1, c2 = st.columns(2)
    race_date = c1.date_input(
        "Fecha de la maratón",
        value=_as_date(saved.get("race_date"), DEFAULT_RACE_DATE),
        help="La fecha inicial es editable. Confirma la fecha oficial de la organización antes de usarla.",
    )
    goal = c2.selectbox(
        "Prioridad",
        ["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Por definir"],
        index=["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Por definir"].index(saved.get("goal", "Completar sano")) if saved.get("goal", "Completar sano") in ["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Por definir"] else 0,
    )
    available_days = st.multiselect(
        "Días posibles para correr",
        DAYS,
        default=[d for d in saved.get("available_days", ["Martes", "Jueves", "Domingo"]) if d in DAYS],
    )
    submitted = st.form_submit_button("Guardar objetivo", type="primary")
if submitted:
    set_profile_value(RACE_KEY, {"race_date": race_date.isoformat(), "goal": goal, "available_days": available_days})
    st.success("Objetivo guardado en Supabase.")
    st.rerun()

remaining = (race_date - date.today()).days
c1, c2, c3 = st.columns(3)
c1.metric("Cuenta regresiva", f"{max(remaining, 0)} días" if remaining >= 0 else "Fecha pasada")
c2.metric("Semanas disponibles", max(0, math.ceil(remaining / 7)))
c3.metric("Prioridad", goal)
if race_date == DEFAULT_RACE_DATE:
    st.caption("La fecha mostrada es una referencia editable, no una confirmación de la fecha oficial.")

st.divider()
st.subheader("Carga de entrenamiento reciente")
try:
    activities = get_activities(start_date=(date.today() - timedelta(days=42)).isoformat(), end_date=date.today().isoformat(), descending=False)
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
    last7 = df[df["activity_date"] >= pd.Timestamp(date.today() - timedelta(days=6))]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Km últimos 7 días", f"{last7['distance_km'].sum():.1f}")
    c2.metric("Km últimos 42 días", f"{df['distance_km'].sum():.1f}")
    c3.metric("Fondo más largo", f"{df['distance_km'].max():.1f} km")
    c4.metric("Sesiones · 7 días", len(last7))
    weekly = df.groupby("week", as_index=False)["distance_km"].sum()
    st.bar_chart(weekly.set_index("week"))
    pain_rows = [x for x in runs if max(int(x.get("pain_during") or 0), int(x.get("pain_after") or 0)) >= 4]
    if pain_rows:
        st.warning(f"Hay {len(pain_rows)} registro(s) con dolor durante o después ≥4/10. No aumentes la carga automáticamente; revisa evolución y síntomas.")
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
