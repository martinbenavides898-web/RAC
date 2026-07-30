from datetime import date, datetime

import streamlit as st

from rac_core.db import add_activity, get_shoes
from rac_core.metrics import pace_text
from rac_core.ui_helpers import page_header

page_header("Registrar entrenamiento", "Demora menos de un minuto; los campos avanzados son opcionales.")

surface = st.selectbox("Superficie", ["Cinta", "Calle", "Parque", "Maicillo", "Pista", "Sendero", "Otra"])
shoes = get_shoes(active_only=True)
shoe_labels = [f'{s["nickname"]} · {s["total_km"]:.1f} km' for s in shoes]

suggested_nickname = "Ghost antiguas" if surface == "Cinta" else "Superblast"
suggested_index = next((i for i, s in enumerate(shoes) if s["nickname"] == suggested_nickname), 0)
st.caption(f"RAC sugiere **{suggested_nickname}** para esta superficie. Puedes cambiarla.")

with st.form("run_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    activity_date = c1.date_input("Fecha", value=date.today())
    activity_time = c2.time_input("Hora", value=datetime.now().time().replace(second=0, microsecond=0))

    c1, c2, c3 = st.columns(3)
    activity_type = c1.selectbox(
        "Tipo",
        ["Rodaje suave", "Fondo", "Cinta suave", "Progresivo", "Intervalos", "Recuperación", "Otro"],
    )
    distance_km = c2.number_input("Distancia (km)", min_value=0.10, max_value=100.0, value=5.0, step=0.10)
    duration_min = c3.number_input("Duración (min)", min_value=1.0, max_value=600.0, value=35.0, step=1.0)

    st.caption(f"Ritmo calculado: **{pace_text(distance_km, duration_min)}**")

    c1, c2 = st.columns(2)
    shoe_label = c1.selectbox("Zapatillas", shoe_labels, index=suggested_index)
    planned_status = c2.selectbox(
        "Relación con el plan",
        ["Plan completado", "Plan modificado", "Entrenamiento espontáneo", "Sesión incompleta"],
    )

    st.markdown("#### Esfuerzo y dolor")
    c1, c2, c3, c4 = st.columns(4)
    rpe = c1.slider("Esfuerzo RPE", 1, 10, 5)
    pain_before = c2.slider("Dolor antes", 0, 10, 0)
    pain_during = c3.slider("Dolor durante", 0, 10, 0)
    pain_after = c4.slider("Dolor después", 0, 10, 0)
    pain_location = st.text_input("Ubicación del dolor, si hubo", placeholder="Ej.: ambos tobillos, tibia derecha...")

    with st.expander("Datos del reloj o aplicación (opcionales)"):
        c1, c2, c3, c4 = st.columns(4)
        avg_hr = c1.number_input("FC promedio", min_value=0, max_value=240, value=0)
        max_hr = c2.number_input("FC máxima", min_value=0, max_value=240, value=0)
        elevation = c3.number_input("Desnivel positivo (m)", min_value=0.0, max_value=10000.0, value=0.0)
        cadence = c4.number_input("Cadencia (spm)", min_value=0.0, max_value=250.0, value=0.0)

    notes = st.text_area(
        "¿Cómo se sintió?",
        placeholder="Ej.: primeros 2 km pesados, después cómodo; terminé entero y sin dolor...",
    )
    submitted = st.form_submit_button("Guardar entrenamiento", type="primary", use_container_width=True)

if submitted:
    selected_shoe = shoes[shoe_labels.index(shoe_label)]
    activity_id = add_activity(
        {
            "activity_date": activity_date.isoformat(),
            "activity_time": activity_time.strftime("%H:%M"),
            "activity_type": activity_type,
            "surface": surface,
            "distance_km": float(distance_km),
            "duration_min": float(duration_min),
            "avg_hr": int(avg_hr) or None,
            "max_hr": int(max_hr) or None,
            "elevation_gain_m": float(elevation) or None,
            "cadence_spm": float(cadence) or None,
            "rpe": int(rpe),
            "pain_before": int(pain_before),
            "pain_during": int(pain_during),
            "pain_after": int(pain_after),
            "pain_location": pain_location.strip(),
            "shoe_id": selected_shoe["id"],
            "planned_status": planned_status,
            "notes": notes.strip(),
        }
    )
    st.success(f"Entrenamiento #{activity_id} guardado.")
    if pain_during >= 4 or pain_after >= 4:
        st.warning("Se registró dolor relevante. RAC no debería aumentar la carga hasta revisar su evolución.")
    elif rpe >= 9:
        st.info("Fue una sesión casi máxima. Una buena sesión no obliga a aumentar la siguiente.")
    else:
        st.info("Registro completo. El análisis con IA se agregará en una etapa posterior.")
