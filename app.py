import streamlit as st

from rac_core.db import init_db
from rac_core.theme import apply_global_theme

st.set_page_config(
    page_title="RAC — Running Assist Coach",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_theme()

try:
    init_db()
except Exception as exc:
    st.error("RAC no pudo conectarse a Supabase.")
    st.exception(exc)
    st.stop()

st.sidebar.markdown('<div class="rac-sidebar-logo">RAC</div>', unsafe_allow_html=True)
st.sidebar.caption("Running Assist Coach · v0.4 visual · Gemini")
st.sidebar.success(
    "Supabase activo. Gemini es el coach IA; RAC conserva datos, perfil, memorias y análisis estructurados."
)

pages = {
    "RAC": [
        st.Page("ui/dashboard.py", title="Hoy", icon="🏠", default=True),
        st.Page("ui/register_run.py", title="Registrar entrenamiento", icon="➕"),
        st.Page("ui/context_day.py", title="Sick / estudio / descanso", icon="🧠"),
        st.Page("ui/coach.py", title="Coach IA", icon="🤖"),
    ],
    "Seguimiento": [
        st.Page("ui/weekly_report.py", title="Reporte semanal", icon="📊"),
        st.Page("ui/shoes.py", title="Zapatillas", icon="👟"),
        st.Page("ui/history.py", title="Historial", icon="🗓️"),
    ],
    "Memoria y configuración": [
        st.Page("ui/memory.py", title="Memoria RAC", icon="🧠"),
        st.Page("ui/profile.py", title="Perfil RAC", icon="⚙️"),
        st.Page("ui/backup.py", title="Respaldo", icon="💾"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
