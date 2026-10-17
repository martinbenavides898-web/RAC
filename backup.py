from __future__ import annotations

import json
import uuid
import pandas as pd
import streamlit as st

from rac_core.db import client, database_label, export_all
from rac_core.gdrive import (
    build_backup_envelope,
    get_drive_status,
    upload_verified_backup,
    verify_backup_in_sandbox,
)
from rac_core.time_utils import now_cl
from rac_core.ui_helpers import page_header

page_header(
    "Google Drive, Respaldos y Privacidad",
    "Fuente de verdad en Supabase PostgreSQL · Respaldo verificado por SHA-256 en Google Drive.",
)

drive_status = get_drive_status()

if drive_status["connected"]:
    st.success(f"Google Drive conectado: {drive_status['user']} · Modo: {drive_status['mode']}")
else:
    st.warning(drive_status["message"])
    with st.expander("Instrucciones de activación de Google Drive API v3 (OAuth 2.0)"):
        st.markdown(
            """
            1. En **Google Cloud Console**, habilita **Google Drive API** y configura la pantalla de consentimiento OAuth.
            2. Genera un `refresh_token` OAuth con el alcance `https://www.googleapis.com/auth/drive.file`.
            3. Agrega en Streamlit Cloud → **Settings → Secrets** (o `.streamlit/secrets.toml` local; nunca en GitHub):
            ```toml
            [gdrive]
            client_id = "TU_CLIENT_ID"
            client_secret = "TU_CLIENT_SECRET"
            refresh_token = "TU_REFRESH_TOKEN"
            root_folder_id = "ID_CARPETA_PADRE_OPCIONAL"
            ```
            """
        )

tab_drive, tab_sandbox, tab_local, tab_privacy = st.tabs(
    ["Respaldar en Google Drive", "Verificar Restauración (Sandbox)", "Exportación Local", "Historial y Privacidad"]
)

with tab_drive:
    backup_type = st.selectbox(
        "Categoría del respaldo",
        ["manual", "daily", "weekly", "pre_migration"],
        format_func=lambda x: {
            "manual": "Manual (bajo demanda)",
            "daily": "Diario (RAC_2/backups/daily)",
            "weekly": "Semanal (RAC_2/backups/weekly)",
            "pre_migration": "Pre-migración (RAC_2/backups/pre_migration)",
        }[x],
    )
    if st.button(
        "Respaldar ahora en Google Drive",
        type="primary",
        disabled=not drive_status["connected"],
        use_container_width=True,
    ):
        with st.spinner("Extrayendo tablas, calculando SHA-256 y verificando subida en Google Drive..."):
            raw_data = export_all()
            b_uuid = str(uuid.uuid4())
            try:
                res = upload_verified_backup(raw_data, backup_type=backup_type)
                client().table("backup_logs").insert(
                    {
                        "backup_uuid": b_uuid,
                        "backup_type": backup_type,
                        "storage_target": "google_drive",
                        "drive_file_id": res["drive_file_id"],
                        "drive_folder_path": res["drive_folder_path"],
                        "file_name": res["file_name"],
                        "file_size_bytes": res["file_size_bytes"],
                        "sha256_hash": res["sha256_hash"],
                        "manifest_json": res["manifest"],
                        "verified": True,
                        "status": "verified",
                    }
                ).execute()
                st.success(
                    f"Respaldo verificado en Google Drive: `{res['drive_folder_path']}/{res['file_name']}` "
                    f"({res['file_size_bytes']:,} bytes · SHA-256: `{res['sha256_hash'][:16]}...`)."
                )
            except Exception as exc:
                st.error(f"El respaldo en Google Drive falló y quedó marcado para reintento: {exc}")

with tab_sandbox:
    st.markdown("#### Prueba de Restauración en Entorno Aislado (No Destructiva)")
    st.caption(
        "Sube un archivo `.json` de respaldo RAC 2.0 para comprobar su integridad criptográfica SHA-256 "
        "y verificar cuántas filas se recuperarían sin sobrescribir la base de datos activa."
    )
    uploaded_backup = st.file_uploader("Seleccionar archivo de respaldo (.json)", type=["json"])
    if uploaded_backup is not None:
        if st.button("Ejecutar verificación de restauración aislada", type="primary"):
            try:
                report = verify_backup_in_sandbox(uploaded_backup.getvalue())
                if report["sandbox_passed"]:
                    st.success("Integridad SHA-256 confirmada. El respaldo es 100% restaurable.")
                else:
                    st.error("Alerta de integridad: el hash del archivo no coincide o faltan tablas.")
                st.json(report)
            except Exception as exc:
                st.error(f"Archivo de respaldo inválido o corrupto: {exc}")

with tab_local:
    raw_data = export_all()
    pkg_bytes, manifest, pkg_sha = build_backup_envelope(raw_data, "manual")
    st.caption(f"Hash SHA-256 del paquete actual: `{pkg_sha}`")
    st.download_button(
        "Descargar paquete completo RAC 2.0 (.json con manifiesto)",
        data=pkg_bytes,
        file_name=f"rac2_backup_local_{now_cl().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        type="primary",
        use_container_width=True,
    )
    if raw_data.get("activities"):
        st.download_button(
            "Descargar entrenamientos (.csv)",
            data=pd.DataFrame(raw_data["activities"]).to_csv(index=False).encode("utf-8-sig"),
            file_name="rac2_activities.csv",
            mime="text/csv",
            use_container_width=True,
        )

with tab_privacy:
    st.markdown("#### Estado de Persistencia y Privacidad")
    st.write(f"- **Motor primario:** {database_label()}")
    st.write("- **Política de contexto IA:** Solo se envían a Gemini datos deportivos compactos (14 días, perfil y memorias activas).")
    st.write("- **Protección de tokens:** Ni las claves de Supabase ni las de Google Drive se exponen en el frontend.")
