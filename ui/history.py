import pandas as pd
import streamlit as st

from rac_core.db import delete_activity, query
from rac_core.metrics import pace_text
from rac_core.ui_helpers import page_header

page_header("Historial", "Entrenamientos y contexto en orden cronológico.")

activities = query(
    """
    SELECT a.*, s.nickname AS shoe_name
    FROM activities a LEFT JOIN shoes s ON s.id = a.shoe_id
    ORDER BY activity_date DESC, activity_time DESC, a.id DESC
    """
)

if not activities:
    st.info("No hay entrenamientos todavía.")
else:
    df = pd.DataFrame(
        [
            {
                "ID": a["id"], "Fecha": a["activity_date"], "Hora": a["activity_time"],
                "Tipo": a["activity_type"], "Superficie": a["surface"],
                "Distancia": a["distance_km"], "Ritmo": pace_text(a["distance_km"], a["duration_min"]),
                "RPE": a["rpe"], "Dolor": max(a["pain_before"], a["pain_during"], a["pain_after"]),
                "Zapatillas": a.get("shoe_name") or "—",
            }
            for a in activities
        ]
    )
    st.dataframe(df, hide_index=True, use_container_width=True)

    with st.expander("Eliminar un registro incorrecto"):
        activity_id = st.selectbox("ID del entrenamiento", [a["id"] for a in activities])
        confirm = st.checkbox("Confirmo que quiero eliminarlo")
        if st.button("Eliminar", disabled=not confirm):
            delete_activity(int(activity_id))
            st.success("Registro eliminado. Recarga la página.")

st.subheader("Eventos de contexto")
events = query("SELECT * FROM context_events ORDER BY event_date DESC, id DESC")
if events:
    st.dataframe(pd.DataFrame(events), hide_index=True, use_container_width=True)
else:
    st.caption("No hay Sick Days, días de estudio ni descansos registrados.")
