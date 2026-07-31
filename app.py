import streamlit as st

from rac_core.db import init_db
from rac_core.theme import apply_global_theme

st.set_page_config(
    page_title="RAC — Running Assist Coach",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_theme()

try:
    init_db()
except Exception as exc:
    st.error("RAC no pudo conectarse a Supabase.")
    st.exception(exc)
    st.stop()

st.sidebar.markdown(
    """
    <div class="rac-sidebar-meta">
        <div class="rac-sidebar-footer-logo">RAC</div>
        <div class="rac-sidebar-version">Running Assist Coach · v0.4.2 visual · Gemini</div>
        <div class="rac-sidebar-status">
            Supabase y Gemini están activos. Tus datos, perfil, memorias y análisis permanecen conectados.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pages = {
    "RAC": [
        st.Page("ui/dashboard.py", title="Hoy", default=True),
        st.Page("ui/register_run.py", title="Registrar entrenamiento"),
        st.Page("ui/context_day.py", title="Sick / estudio / descanso"),
        st.Page("ui/coach.py", title="Coach IA"),
    ],
    "Seguimiento": [
        st.Page("ui/weekly_report.py", title="Reporte semanal"),
        st.Page("ui/shoes.py", title="Zapatillas"),
        st.Page("ui/history.py", title="Historial"),
    ],
    "Memoria y configuración": [
        st.Page("ui/memory.py", title="Memoria RAC"),
        st.Page("ui/profile.py", title="Perfil RAC"),
        st.Page("ui/backup.py", title="Respaldo"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
