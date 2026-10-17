from __future__ import annotations

from datetime import date, datetime
import json

import pandas as pd
import streamlit as st

from rac_core.db import get_activities, get_profile, set_profile_value
from rac_core.plan_engine import build_week_plan, summarize_training
from rac_core.terrain import analyze_gpx_bytes
from rac_core.ui_helpers import page_header

page_header(
    "RAC 2.0 · Centro de preparación 42K",
    "Planificación adaptativa inicial, datos históricos y análisis de recorrido. Las recomendaciones son apoyo deportivo, no diagnóstico médico.",
)

profile = get_profile()
config = profile.get("marathon_config") or {}
runner = profile.get("runner_profile") or {}

st.subheader("Tu objetivo")
with st.form("marathon_config_form"):
    c1, c2, c3 = st.columns(3)
    race_date = c1.date_input(
        "Fecha de la Maratón de Santiago 2027",
        value=date.fromisoformat(config.get("race_date", "2027-04-18")),
        help="Confirma la fecha oficial cuando esté publicada; esta fecha inicial es editable y no debe asumirse oficial.",
    )
    goal = c2.selectbox(
        "Objetivo principal",
        ["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Otro / por definir"],
        index=["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Otro / por definir"].index(config.get("goal", "Completar sano")) if config.get("goal", "Completar sano") in ["Completar sano", "Completar disfrutando", "Buscar sub-4:30", "Buscar sub-4:00", "Otro / por definir"] else 0,
    )
    available_days = c3.multiselect(
        "Días posibles para correr",
        ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        default=config.get("available_days", ["Martes", "Jueves", "Sábado", "Domingo"]),
    )
    saved = st.form_submit_button("Guardar configuración", type="primary")
if saved:
    config.update({"race_date": race_date.isoformat(), "goal": goal, "available_days": available_days})
    set_profile_value("marathon_config", config)
    st.success("Configuración guardada en Supabase.")
    st.rerun()

remaining = (race_date - date.today()).days
c1, c2, c3 = st.columns(3)
c1.metric("Cuenta regresiva", f"{max(0, remaining)} días" if remaining >= 0 else "Fecha pasada")
c2.metric("Semanas disponibles", f"{max(0, remaining // 7)}")
c3.metric("Objetivo", goal)
if race_date == date(2027, 4, 18):
    st.caption("Nota: 18 de abril es solo una fecha inicial editable, no una confirmación de la fecha oficial de la carrera.")

activities = get_activities(descending=True, limit=500)
summary = summarize_training(activities)
st.subheader("Tu carga reciente")
cols = st.columns(4)
cols[0].metric("Promedio semanal · 4 sem", f"{summary['weekly_km_4w_avg']} km")
cols[1].metric("Últimos 7 días", f"{summary['last7_km']} km")
cols[2].metric("Fondo reciente", f"{summary['longest_recent_km']} km")
cols[3].metric("Sesiones · 7 días", summary["sessions_last7"])
if summary["sample_28d"] < 3:
    st.info("Todavía hay pocos registros recientes para una planificación precisa. Registra entrenamientos reales antes de confiar en las distancias sugeridas.")

st.subheader("Semana adaptativa")
plan = build_week_plan(
    activities,
    config.get("available_days", ["Martes", "Jueves", "Sábado", "Domingo"]),
    race_date=race_date,
    race_goal=goal,
)
st.markdown(f"### {plan['status']}")
st.write(plan["reason"])
st.metric("Volumen orientativo de la semana", f"{plan['target_km']} km")
plan_df = pd.DataFrame(plan["sessions"])
plan_df["distance_km"] = plan_df["distance_km"].map(lambda x: f"{x:.1f} km")
st.dataframe(plan_df.rename(columns={"day": "Día", "type": "Sesión", "distance_km": "Distancia", "note": "Indicaciones"}), use_container_width=True, hide_index=True)
st.caption("Este es un primer motor conservador basado en tus registros. No reemplaza todavía el juicio completo de Gemini ni debe usarse para entrenar con dolor.")

st.subheader("Analizar recorrido GPX")
st.write("Sube un GPX del recorrido de la carrera o de una ruta de entrenamiento para estimar distancia, desnivel y perfil de pendientes.")
upload = st.file_uploader("Archivo GPX", type=["gpx"], key="race_gpx_upload")
if upload is not None:
    try:
        terrain = analyze_gpx_bytes(upload.getvalue())
        a, b, c, d = st.columns(4)
        a.metric("Distancia", f"{terrain['total_distance_km']:.2f} km")
        b.metric("Desnivel positivo", f"+{terrain['elevation_gain_m']:.0f} m")
        c.metric("Desnivel negativo", f"−{terrain['elevation_loss_m']:.0f} m")
        d.metric("Altitud", f"{terrain['min_altitude_m']}–{terrain['max_altitude_m']} m" if terrain['min_altitude_m'] is not None else "Sin datos")
        segments = terrain.get("segments", [])
        if segments:
            st.dataframe(pd.DataFrame(segments).rename(columns={"km": "Km", "net_elevation_m": "Cambio neto (m)", "gain_m": "Subida (m)", "loss_m": "Bajada (m)", "grade_pct": "Pendiente (%)", "classification": "Tipo de tramo"}), use_container_width=True, hide_index=True)
        if st.button("Guardar este recorrido en RAC", type="primary"):
            saved_routes = profile.get("gpx_routes") or []
            saved_routes = [r for r in saved_routes if r.get("file_sha256") != terrain["file_sha256"]]
            saved_routes.append({"name": upload.name, "analyzed_at": datetime.now().isoformat(timespec="seconds"), **terrain})
            set_profile_value("gpx_routes", saved_routes[-20:])
            st.success("Análisis del recorrido guardado en Supabase.")
    except Exception as exc:
        st.error(f"No pude analizar este GPX: {exc}")

saved_routes = profile.get("gpx_routes") or []
if saved_routes:
    with st.expander(f"Recorridos guardados ({len(saved_routes)})"):
        for route in reversed(saved_routes):
            st.markdown(f"**{route.get('name', 'GPX')}** · {route.get('total_distance_km', 0)} km · +{route.get('elevation_gain_m', 0)} m")
            st.caption(f"Analizado: {route.get('analyzed_at', 'fecha no disponible')} · SHA-256: {route.get('file_sha256', '')[:16]}…")
