from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
ROOT_NAME = "RAC_2"
BACKUP_CATEGORIES = {"manual", "daily", "weekly", "pre_migration"}


def _config() -> dict[str, Any]:
    try:
        config = dict(st.secrets["gdrive"])
    except (KeyError, FileNotFoundError) as exc:
        raise RuntimeError("Falta la sección [gdrive] en Streamlit Secrets.") from exc
    for key in ("client_id", "client_secret", "refresh_token"):
        if not str(config.get(key, "")).strip():
            raise RuntimeError(f"Falta gdrive.{key} en Streamlit Secrets.")
    return config


def _service():
    config = _config()
    credentials = Credentials(
        token=None,
        refresh_token=str(config["refresh_token"]).strip(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=str(config["client_id"]).strip(),
        client_secret=str(config["client_secret"]).strip(),
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def get_drive_status() -> dict[str, Any]:
    try:
        service = _service()
        about = service.about().get(fields="user(displayName,emailAddress)").execute()
        user = (about.get("user") or {}).get("emailAddress") or (about.get("user") or {}).get("displayName") or "Cuenta conectada"
        return {"connected": True, "user": user, "mode": "OAuth 2.0", "message": "Google Drive conectado."}
    except Exception as exc:
        return {"connected": False, "user": None, "mode": "OAuth 2.0", "message": f"Google Drive no está conectado: {exc}"}


def _find_or_create_folder(service, name: str, parent_id: str | None) -> str:
    escaped_name = name.replace("'", "\\'")
    query = f"name = '{escaped_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    result = service.files().list(q=query, spaces="drive", fields="files(id,name)", pageSize=100).execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"]
    metadata: dict[str, Any] = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    return service.files().create(body=metadata, fields="id").execute()["id"]


def _folder_path(service, backup_type: str) -> tuple[str, str]:
    if backup_type not in BACKUP_CATEGORIES:
        raise ValueError(f"Categoría de respaldo no válida: {backup_type}")
    config = _config()
    parent = str(config.get("root_folder_id", "")).strip() or None
    root_id = _find_or_create_folder(service, ROOT_NAME, parent)
    backups_id = _find_or_create_folder(service, "backups", root_id)
    category_id = _find_or_create_folder(service, backup_type, backups_id)
    return category_id, f"{ROOT_NAME}/backups/{backup_type}"


def build_backup_envelope(raw_data: dict[str, Any], backup_type: str = "manual") -> tuple[bytes, dict[str, Any], str]:
    payload_bytes = json.dumps(raw_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    payload_sha = hashlib.sha256(payload_bytes).hexdigest()
    manifest = {
        "format": "rac-backup-envelope-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backup_type": backup_type,
        "payload_sha256": payload_sha,
        "payload_size_bytes": len(payload_bytes),
        "tables": {key: len(value) if isinstance(value, list) else (len(value) if isinstance(value, dict) else None) for key, value in raw_data.items()},
    }
    envelope = {"manifest": manifest, "payload": raw_data}
    package = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return package, manifest, hashlib.sha256(package).hexdigest()


def verify_backup_in_sandbox(package_bytes: bytes) -> dict[str, Any]:
    try:
        envelope = json.loads(package_bytes.decode("utf-8"))
        manifest = envelope["manifest"]
        payload = envelope["payload"]
        actual = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
        required = {"activities", "context_events", "shoes", "profile"}
        missing = sorted(required - set(payload))
        passed = manifest.get("format") == "rac-backup-envelope-v1" and actual == manifest.get("payload_sha256") and not missing
        counts = {key: len(value) if isinstance(value, (list, dict)) else None for key, value in payload.items()}
        return {"sandbox_passed": bool(passed), "hash_matches": actual == manifest.get("payload_sha256"), "missing_required_sections": missing, "record_counts": counts, "payload_sha256": actual}
    except Exception as exc:
        raise ValueError(f"No se pudo validar el paquete RAC: {exc}") from exc


def upload_verified_backup(raw_data: dict[str, Any], backup_type: str = "manual") -> dict[str, Any]:
    service = _service()
    folder_id, folder_path = _folder_path(service, backup_type)
    package, manifest, package_sha = build_backup_envelope(raw_data, backup_type)
    stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    file_name = f"rac_backup_{backup_type}_{stamp}.json"
    media = MediaIoBaseUpload(io.BytesIO(package), mimetype="application/json", resumable=True)
    created = service.files().create(
        body={"name": file_name, "mimeType": "application/json", "parents": [folder_id], "description": f"RAC backup; package_sha256={package_sha}"},
        media_body=media,
        fields="id,name,size,parents",
    ).execute()
    file_id = created["id"]

    # Verify the actual bytes downloaded back from Drive, then verify the payload checksum.
    request = service.files().get_media(fileId=file_id)
    stream = io.BytesIO()
    downloader = MediaIoBaseDownload(stream, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    downloaded = stream.getvalue()
    if hashlib.sha256(downloaded).hexdigest() != package_sha:
        raise RuntimeError("El archivo subido no coincide byte a byte al descargarlo desde Drive.")
    verification = verify_backup_in_sandbox(downloaded)
    if not verification["sandbox_passed"]:
        raise RuntimeError("El archivo subido no pasó la verificación de integridad del contenido.")

    return {
        "drive_file_id": file_id,
        "drive_folder_path": folder_path,
        "file_name": file_name,
        "file_size_bytes": len(package),
        "sha256_hash": package_sha,
        "manifest": manifest,
    }
