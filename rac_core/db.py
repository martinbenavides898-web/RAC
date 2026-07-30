from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def client() -> Client:
    """Create one server-side Supabase client for the Streamlit process."""
    try:
        config = st.secrets["supabase"]
        url = str(config["url"]).strip()
        key = str(config["key"]).strip()
    except (KeyError, FileNotFoundError) as exc:
        raise RuntimeError(
            "Faltan los secretos de Supabase. Configura [supabase] url y key en Streamlit Secrets."
        ) from exc

    if not url or not key:
        raise RuntimeError("La URL o la clave de Supabase están vacías.")

    return create_client(url, key)


def init_db() -> None:
    """Fail early with a clear error if Supabase is not reachable or configured."""
    client().table("profile").select("key").limit(1).execute()


def _flatten_activity(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    shoe = item.pop("shoes", None)
    item["shoe_name"] = shoe.get("nickname") if isinstance(shoe, dict) else None
    return item


def _activities(
    start_date: str | None = None,
    end_date: str | None = None,
    *,
    descending: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    request = client().table("activities").select("*, shoes(nickname)")
    if start_date:
        request = request.gte("activity_date", start_date)
    if end_date:
        request = request.lte("activity_date", end_date)
    request = request.order("activity_date", desc=descending).order(
        "activity_time", desc=descending
    ).order("id", desc=descending)
    if limit is not None:
        request = request.limit(limit)
    response = request.execute()
    return [_flatten_activity(row) for row in (response.data or [])]


def _events(
    start_date: str | None = None,
    end_date: str | None = None,
    *,
    descending: bool = False,
) -> list[dict[str, Any]]:
    request = client().table("context_events").select("*")
    if start_date:
        request = request.gte("event_date", start_date)
    if end_date:
        request = request.lte("event_date", end_date)
    response = request.order("event_date", desc=descending).order(
        "id", desc=descending
    ).execute()
    return list(response.data or [])


def query(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Compatibility layer for the small set of reads used by RAC v0.1 pages."""
    normalized = re.sub(r"\s+", " ", sql.strip().lower())

    if "from activities a" in normalized:
        has_range = "activity_date between ? and ?" in normalized
        descending = "order by activity_date desc" in normalized
        limit = 1 if "limit 1" in normalized else None
        start = str(params[0]) if has_range else None
        end = str(params[1]) if has_range else None
        return _activities(start, end, descending=descending, limit=limit)

    if normalized.startswith("select * from activities"):
        return _activities(descending="desc" in normalized)

    if "from context_events" in normalized:
        has_range = "event_date between ? and ?" in normalized
        start = str(params[0]) if has_range else None
        end = str(params[1]) if has_range else None
        return _events(start, end, descending="desc" in normalized)

    if normalized.startswith("select * from shoes"):
        return list(client().table("shoes").select("*").order("id").execute().data or [])

    if normalized.startswith("select * from profile"):
        return list(client().table("profile").select("*").order("key").execute().data or [])

    raise ValueError(f"Consulta no soportada por la capa Supabase de RAC: {normalized}")


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    """Compatibility layer for the one generic write used by the shoes page."""
    normalized = re.sub(r"\s+", " ", sql.strip().lower())
    if normalized.startswith("insert into shoes"):
        brand, model, nickname, use_context, initial_km, _created_at = params
        response = client().table("shoes").insert(
            {
                "brand": brand,
                "model": model,
                "nickname": nickname,
                "use_context": use_context,
                "initial_km": float(initial_km),
                "active": True,
            }
        ).execute()
        if not response.data:
            raise RuntimeError("Supabase no devolvió la zapatilla guardada.")
        return int(response.data[0]["id"])

    raise ValueError(f"Escritura no soportada por la capa Supabase de RAC: {normalized}")


def get_shoes(active_only: bool = True) -> list[dict[str, Any]]:
    request = client().table("shoes").select("*")
    if active_only:
        request = request.eq("active", True)
    shoes = list(request.order("active", desc=True).order("nickname").execute().data or [])

    activities = client().table("activities").select("shoe_id,distance_km").execute().data or []
    totals: dict[int, float] = {}
    for activity in activities:
        shoe_id = activity.get("shoe_id")
        if shoe_id is not None:
            totals[int(shoe_id)] = totals.get(int(shoe_id), 0.0) + float(
                activity.get("distance_km") or 0
            )

    for shoe in shoes:
        shoe["total_km"] = float(shoe.get("initial_km") or 0) + totals.get(
            int(shoe["id"]), 0.0
        )
    return shoes


def add_activity(data: dict[str, Any]) -> int:
    payload = {
        "activity_date": data["activity_date"],
        "activity_time": data.get("activity_time"),
        "activity_type": data["activity_type"],
        "surface": data["surface"],
        "distance_km": data["distance_km"],
        "duration_min": data["duration_min"],
        "avg_hr": data.get("avg_hr"),
        "max_hr": data.get("max_hr"),
        "elevation_gain_m": data.get("elevation_gain_m"),
        "cadence_spm": data.get("cadence_spm"),
        "rpe": data["rpe"],
        "pain_before": data["pain_before"],
        "pain_during": data["pain_during"],
        "pain_after": data["pain_after"],
        "pain_location": data.get("pain_location", ""),
        "shoe_id": data.get("shoe_id"),
        "planned_status": data["planned_status"],
        "notes": data.get("notes", ""),
    }
    response = client().table("activities").insert(payload).execute()
    if not response.data:
        raise RuntimeError("Supabase no devolvió el entrenamiento guardado.")
    return int(response.data[0]["id"])


def add_context_event(data: dict[str, Any]) -> int:
    payload = {
        "event_date": data["event_date"],
        "event_type": data["event_type"],
        "planned_training": bool(data.get("planned_training", False)),
        "sleep_hours": data.get("sleep_hours"),
        "severity": data.get("severity"),
        "stress": data.get("stress"),
        "study_hours": data.get("study_hours"),
        "symptoms": data.get("symptoms", ""),
        "notes": data.get("notes", ""),
    }
    response = client().table("context_events").insert(payload).execute()
    if not response.data:
        raise RuntimeError("Supabase no devolvió el evento guardado.")
    return int(response.data[0]["id"])


def get_profile() -> dict[str, Any]:
    rows = client().table("profile").select("key,value_json").execute().data or []
    return {row["key"]: row["value_json"] for row in rows}


def set_profile_value(key: str, value: Any) -> None:
    client().table("profile").upsert(
        {
            "key": key,
            "value_json": value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="key",
    ).execute()


def delete_activity(activity_id: int) -> None:
    client().table("activities").delete().eq("id", activity_id).execute()


def database_path() -> str:
    return "Supabase PostgreSQL · persistencia activa"
