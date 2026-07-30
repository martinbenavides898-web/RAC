from pathlib import Path

import streamlit as st

from rac_core.db import init_db

APP_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="RAC — Running App Coach",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

st.sidebar.title("🏃 RAC")
st.sidebar.caption("Running App Coach · v0.1")
st.sidebar.info(
    "Versión inicial: registro, contexto, zapatillas y reporte semanal. "
    "La integración con IA y una base persistente vendrán en las siguientes etapas."
)

pages = {
    "RAC": [
        st.Page("ui/dashboard.py", title="Inicio", icon="🏠", default=True),
        st.Page("ui/register_run.py", title="Registrar entrenamiento", icon="➕"),
        st.Page("ui/context_day.py", title="Sick / estudio / descanso", icon="🧠"),
    ],
    "Seguimiento": [
        st.Page("ui/weekly_report.py", title="Reporte semanal", icon="📊"),
        st.Page("ui/shoes.py", title="Zapatillas", icon="👟"),
        st.Page("ui/history.py", title="Historial", icon="🗓️"),
    ],
    "Configuración": [
        st.Page("ui/profile.py", title="Perfil RAC", icon="⚙️"),
        st.Page("ui/backup.py", title="Respaldo", icon="💾"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
