import json
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

from rac_core.db import database_path, query
from rac_core.ui_helpers import local_storage_warning, page_header

page_header("Respaldo", "Descarga tus datos hasta que conectemos la base persistente.")
local_storage_warning()

activities = query("SELECT * FROM activities ORDER BY activity_date")
events = query("SELECT * FROM context_events ORDER BY event_date")
shoes = query("SELECT * FROM shoes ORDER BY id")
profile = query("SELECT * FROM profile ORDER BY key")

payload = {
    "exported_at": datetime.now().isoformat(timespec="seconds"),
    "activities": activities,
    "context_events": events,
    "shoes": shoes,
    "profile": profile,
}

st.download_button(
    "Descargar respaldo JSON",
    data=json.dumps(payload, ensure_ascii=False, indent=2),
    file_name=f"rac_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
    mime="application/json",
    type="primary",
)

if activities:
    st.download_button(
        "Descargar entrenamientos CSV",
        data=pd.DataFrame(activities).to_csv(index=False).encode("utf-8-sig"),
        file_name="rac_entrenamientos.csv",
        mime="text/csv",
    )

st.caption(f"Base activa: {database_path()}")
