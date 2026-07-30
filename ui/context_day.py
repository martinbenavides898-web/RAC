from datetime import date

import streamlit as st

from rac_core.db import add_context_event
from rac_core.ui_helpers import page_header

page_header("Contexto del día", "Una sesión omitida no es una deuda deportiva.")

sick_tab, study_tab, rest_tab = st.tabs(["🤒 Sick Day", "📚 Día de estudio", "🛌 Descanso"])

with sick_tab:
    with st.form("sick_form"):
        event_date = st.date_input("Fecha", value=date.today(), key="sick_date")
        planned = st.checkbox("¿Había entrenamiento planificado?", key="sick_planned")
        c1, c2, c3 = st.columns(3)
        sleep = c1.number_input("Horas de sueño", 0.0, 16.0, 6.0, 0.5, key="sick_sleep")
        severity = c2.slider("Malestar general", 1, 5, 2)
        stress = c3.slider("Estrés", 1, 5, 2, key="sick_stress")
        symptoms = st.text_input("Síntomas generales", placeholder="Ej.: congestión, dolor de garganta...")
        notes = st.text_area("Notas")
        submit = st.form_submit_button("Registrar Sick Day", type="primary")
    if submit:
        add_context_event(
            {
                "event_date": event_date.isoformat(), "event_type": "Sick day",
                "planned_training": planned, "sleep_hours": sleep,
                "severity": severity, "stress": stress, "symptoms": symptoms, "notes": notes,
            }
        )
        st.success("Sick Day registrado. RAC considerará esta interrupción como contexto, no como fracaso.")

with study_tab:
    with st.form("study_form"):
        event_date = st.date_input("Fecha", value=date.today(), key="study_date")
        planned = st.checkbox("¿Había entrenamiento planificado?", key="study_planned")
        c1, c2, c3 = st.columns(3)
        sleep = c1.number_input("Horas de sueño", 0.0, 16.0, 6.0, 0.5, key="study_sleep")
        study_hours = c2.number_input("Horas de estudio", 0.0, 24.0, 4.0, 0.5)
        stress = c3.slider("Carga/estrés académico", 1, 5, 3, key="study_stress")
        notes = st.text_area("¿Qué pasó?", placeholder="Ej.: prueba al día siguiente; tuve que salvar el estudio...")
        submit = st.form_submit_button("Registrar Día de estudio", type="primary")
    if submit:
        add_context_event(
            {
                "event_date": event_date.isoformat(), "event_type": "Día de estudio",
                "planned_training": planned, "sleep_hours": sleep,
                "study_hours": study_hours, "stress": stress, "notes": notes,
            }
        )
        st.success("Día de estudio registrado. RAC no intentará 'pagar' automáticamente la sesión perdida.")

with rest_tab:
    with st.form("rest_form"):
        event_date = st.date_input("Fecha", value=date.today(), key="rest_date")
        planned = st.checkbox("¿Había entrenamiento planificado?", key="rest_planned")
        c1, c2 = st.columns(2)
        sleep = c1.number_input("Horas de sueño", 0.0, 16.0, 7.0, 0.5, key="rest_sleep")
        stress = c2.slider("Estrés general", 1, 5, 2, key="rest_stress")
        notes = st.text_area("Notas", key="rest_notes")
        submit = st.form_submit_button("Registrar descanso", type="primary")
    if submit:
        add_context_event(
            {
                "event_date": event_date.isoformat(), "event_type": "Descanso",
                "planned_training": planned, "sleep_hours": sleep,
                "stress": stress, "notes": notes,
            }
        )
        st.success("Descanso registrado.")
