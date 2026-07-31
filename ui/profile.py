import streamlit as st

from rac_core.db import get_profile, set_profile_value
from rac_core.ui_helpers import page_header

page_header("Perfil RAC", "Memoria estable y editable del corredor y del coach.")

profile = get_profile()

basic_tab, running_tab, coach_tab, raw_tab = st.tabs(
    ["Corredor", "Historial y disponibilidad", "Coach", "Memoria estructurada"]
)

with basic_tab:
    runner = profile.get("runner_profile") or {}
    c1, c2, c3 = st.columns(3)
    height = c1.number_input("Altura (cm)", 100, 230, int(runner.get("height_cm", 176)))
    current_weight = c2.number_input(
        "Peso actual (kg)", 40.0, 250.0, float(runner.get("current_weight_kg", 85)), 0.1
    )
    current_pain = c3.slider("Dolor actual general", 0, 10, int(runner.get("current_pain", 0)))
    target = runner.get("target_weight_range_kg") or [77, 80]
    c1, c2 = st.columns(2)
    target_min = c1.number_input("Peso objetivo mínimo", 40.0, 250.0, float(target[0]), 0.5)
    target_max = c2.number_input("Peso objetivo máximo", 40.0, 250.0, float(target[1]), 0.5)
    return_started = st.text_input("Inicio del retorno", value=str(runner.get("return_started", "2026-07-05")))
    current_stage = st.text_area("Etapa actual", value=str(runner.get("current_stage", "")))
    best_stage = st.text_area("Mejor etapa previa", value=str(runner.get("best_stage", "")))

    if st.button("Guardar perfil del corredor", type="primary"):
        set_profile_value(
            "runner_profile",
            {
                "height_cm": height,
                "current_weight_kg": current_weight,
                "target_weight_range_kg": [target_min, target_max],
                "return_started": return_started,
                "best_stage": best_stage,
                "current_stage": current_stage,
                "current_pain": current_pain,
            },
        )
        st.success("Perfil del corredor guardado.")

with running_tab:
    availability = profile.get("availability_profile") or {}
    days = availability.get("running_days") or {}
    martes = st.text_input("Martes", value=str(days.get("martes", "")))
    miercoles = st.text_input("Miércoles", value=str(days.get("miércoles", "")))
    sabado = st.text_input("Sábado", value=str(days.get("sábado", "")))
    sleep_reality = st.number_input(
        "Sueño habitual estimado en periodo universitario",
        0.0,
        16.0,
        float(availability.get("sleep_reality_hours", 6)),
        0.5,
    )
    strength_source = st.text_input(
        "Fuente de fortalecimiento", value=str(availability.get("strength_source", "LagartijApp"))
    )
    home_equipment = st.text_input(
        "Equipo disponible",
        value=", ".join(availability.get("home_equipment") or ["mancuernas de 4 kg"]),
    )
    injury_history = st.text_area(
        "Historial de lesiones/molestias, una por línea",
        value="\n".join(profile.get("injury_history") or []),
        height=160,
    )
    if st.button("Guardar historial y disponibilidad", type="primary"):
        set_profile_value(
            "availability_profile",
            {
                "running_days": {"martes": martes, "miércoles": miercoles, "sábado": sabado},
                "sleep_reality_hours": sleep_reality,
                "strength_source": strength_source,
                "gym_currently": False,
                "home_equipment": [x.strip() for x in home_equipment.split(",") if x.strip()],
            },
        )
        set_profile_value(
            "injury_history", [line.strip() for line in injury_history.splitlines() if line.strip()]
        )
        st.success("Historial y disponibilidad guardados.")

with coach_tab:
    communication = profile.get("communication_profile") or {}
    coach_style = st.text_area("Estilo del coach", value=profile.get("coach_style", ""))
    tone = st.text_area("Tono práctico", value=str(communication.get("tone", "")))
    response_style = st.text_area(
        "Formato de respuesta", value=str(communication.get("response_style", ""))
    )
    interpretation_notes = st.text_area(
        "Cómo interpretar mi forma de escribir, una regla por línea",
        value="\n".join(communication.get("interpretation_notes") or []),
        height=150,
    )
    primary_goal = st.text_area("Objetivo principal", value=profile.get("primary_goal", ""))
    endurance_goal = st.text_area("Objetivo de resistencia", value=profile.get("endurance_goal", ""))
    pace_goal = st.text_area("Objetivo de ritmo", value=profile.get("pace_goal", ""))
    coach_rule = st.text_area("Regla principal", value=profile.get("coach_rule", ""))

    if st.button("Guardar configuración del coach", type="primary"):
        set_profile_value("coach_style", coach_style.strip())
        set_profile_value("primary_goal", primary_goal.strip())
        set_profile_value("endurance_goal", endurance_goal.strip())
        set_profile_value("pace_goal", pace_goal.strip())
        set_profile_value("coach_rule", coach_rule.strip())
        set_profile_value(
            "communication_profile",
            {
                "tone": tone.strip(),
                "response_style": response_style.strip(),
                "language": "Español chileno natural",
                "interpretation_notes": [
                    line.strip() for line in interpretation_notes.splitlines() if line.strip()
                ],
            },
        )
        st.success("Configuración del coach guardada.")

with raw_tab:
    st.json(get_profile())
