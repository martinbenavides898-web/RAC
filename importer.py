from __future__ import annotations

import hashlib
from typing import Any
import pandas as pd


def generate_activity_fingerprint(
    activity_date: str, distance_km: float, duration_min: float, sport: str
) -> str:
    raw = f"{activity_date.strip()} | {sport.strip().lower()} | {round(float(distance_km), 2)} | {round(float(duration_min), 1)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_and_normalize_csv(
    df: pd.DataFrame, source_label: str = "csv_import"
) -> list[dict[str, Any]]:
    """
    Normaliza columnas comunes (español o inglés) a la estructura de `activities` de RAC 2.0.
    """
    col_map = {c.lower().strip(): c for c in df.columns}

    def _pick(*candidates: str) -> str | None:
        for cand in candidates:
            if cand in col_map:
                return col_map[cand]
        return None

    date_col = _pick("activity_date", "fecha", "date", "start_time")
    dist_col = _pick("distance_km", "distancia", "distance", "distancia (km)")
    dur_col = _pick("duration_min", "duracion", "duración", "duration", "moving_time", "tiempo (min)")
    hr_col = _pick("avg_hr", "fc_promedio", "average_heartrate", "heart_rate")
    cad_col = _pick("cadence_spm", "cadencia", "average_cadence")
    type_col = _pick("activity_type", "tipo", "type", "sport")

    if not date_col or not dist_col or not dur_col:
        raise ValueError(
            "El CSV debe incluir al menos columnas equivalentes a Fecha ('date'/'fecha'), "
            "Distancia ('distance_km'/'distancia') y Duración ('duration_min'/'duracion')."
        )

    records: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        raw_date = str(row[date_col])[:10]
        dist_val = float(row[dist_col] or 0.0)

        # Si la distancia viene en metros (ej. > 120), convertir a km
        if dist_val > 120:
            dist_val = round(dist_val / 1000.0, 3)

        dur_val = float(row[dur_col] or 0.0)
        # Si la duración viene en segundos (ej. > 600 min), convertir a minutos
        if dur_val > 600:
            dur_val = round(dur_val / 60.0, 2)

        act_type = (
            str(row[type_col]).strip()
            if type_col and pd.notna(row[type_col])
            else "Rodaje importado"
        )
        fingerprint = generate_activity_fingerprint(
            raw_date, dist_val, dur_val, "Running"
        )

        records.append(
            {
                "activity_date": raw_date,
                "activity_time": "08:00",
                "sport_category": "Running",
                "activity_type": act_type,
                "surface": "Calle",
                "distance_km": dist_val,
                "duration_min": dur_val,
                "avg_hr": int(row[hr_col])
                if hr_col and pd.notna(row[hr_col]) and float(row[hr_col]) > 0
                else None,
                "max_hr": None,
                "elevation_gain_m": None,
                "cadence_spm": float(row[cad_col])
                if cad_col and pd.notna(row[cad_col]) and float(row[cad_col]) > 0
                else None,
                "rpe": 5,
                "pain_before": 0,
                "pain_during": 0,
                "pain_after": 0,
                "pain_location": "",
                "tibial_alert": False,
                "shoe_id": None,
                "planned_status": "Plan completado",
                "data_source": source_label,
                "external_hash": fingerprint,
                "notes": f"Importado desde {source_label}",
            }
        )

    return records
