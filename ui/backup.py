import json
from datetime import datetime

import pandas as pd
import streamlit as st

from rac_core.db import database_label, export_all
from rac_core.ui_helpers import page_header, persistence_status

page_header("Respaldo", "Descarga una copia portable de tus datos cuando quieras.")
persistence_status()

data = export_all()
payload = {
    "exported_at": datetime.now().isoformat(timespec="seconds"),
    **data,
}

st.download_button(
    "Descargar respaldo JSON",
    data=json.dumps(payload, ensure_ascii=False, indent=2, default=str),
    file_name=f"rac_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
    mime="application/json",
    type="primary",
)

if data["activities"]:
    st.download_button(
        "Descargar entrenamientos CSV",
        data=pd.DataFrame(data["activities"]).to_csv(index=False).encode("utf-8-sig"),
        file_name="rac_entrenamientos.csv",
        mime="text/csv",
    )

st.caption(f"Base activa: {database_label()}")
