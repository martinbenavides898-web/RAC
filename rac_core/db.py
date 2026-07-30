from __future__ import annotations

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
    """Fail early if Supabase is unreachable or the tables are unavailable."""
    client().table("profile").select("key").limit(1).execute()


def _flatten_activity(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    shoe = item.pop("shoes", None)
    item["shoe_name"] = shoe.get("nickname") if isinstance(shoe, dict) else None
    return item


def get_activities(
    start_date: str | None = None,
    end_date: str | None = None,
    *,
    descending: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Return activities, optionally filtered by an inclusive date range."""
    request = client().table("activities").select("*, shoes(nickname)")
    if start_date:
        request = request.gte("activity_date", start_date)
    if end_date:
        request = request.lte("activity_date", end_date)

    request = (
        request.order("activity_date", desc=descending)
        .order("activity_time", desc=descending)
        .order("id", desc=descending)
    )
    if limit is not None:
        request = request.limit(limit)

    response = request.execute()
    return [_flatten_activity(row) for row in (response.data or [])]


def get_context_events(
    start_date: str | None = None,
    end_date: str | None = None,
    *,
    descending: bool = False,
) -> list[dict[str, Any]]:
    """Return context events, optionally filtered by an inclusive date range."""
    request = client().table("context_events").select("*")
    if start_date:
        request = request.gte("event_date", start_date)
    if end_date:
        request = request.lte("event_date", end_date)

    response = (
        request.order("event_date", desc=descending)
        .order("id", desc=descending)
        .execute()
    )
    return list(response.data or [])


def get_shoes(active_only: bool = True) -> list[dict[str, Any]]:
    request = client().table("shoes").select("*")
    if active_only:
        request = request.eq("active", True)
    shoes = list(
        request.order("active", desc=True).order("nickname").execute().data or []
    )

    activities = (
        client().table("activities").select("shoe_id,distance_km").execute().data or []
    )
    totals: dict[int, float] = {}
    for activity in activities:
        shoe_id = activity.get("shoe_id")
        if shoe_id is not None:
            numeric_id = int(shoe_id)
            totals[numeric_id] = totals.get(numeric_id, 0.0) + float(
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
        "distance_km": float(data["distance_km"]),
        "duration_min": float(data["duration_min"]),
        "avg_hr": data.get("avg_hr"),
        "max_hr": data.get("max_hr"),
        "elevation_gain_m": data.get("elevation_gain_m"),
        "cadence_spm": data.get("cadence_spm"),
        "rpe": int(data["rpe"]),
        "pain_before": int(data["pain_before"]),
        "pain_during": int(data["pain_during"]),
        "pain_after": int(data["pain_after"]),
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


def add_shoe(data: dict[str, Any]) -> int:
    payload = {
        "brand": data["brand"],
        "model": data["model"],
        "nickname": data["nickname"],
        "use_context": data.get("use_context", ""),
        "initial_km": float(data.get("initial_km", 0)),
        "active": bool(data.get("active", True)),
    }
    response = client().table("shoes").insert(payload).execute()
    if not response.data:
        raise RuntimeError("Supabase no devolvió la zapatilla guardada.")
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


def export_all() -> dict[str, Any]:
    """Return a portable snapshot of every RAC table currently used by the app."""
    return {
        "activities": get_activities(descending=False),
        "context_events": get_context_events(descending=False),
        "shoes": get_shoes(active_only=False),
        "strength_logs": list(
            client().table("strength_logs").select("*").order("log_date").execute().data
            or []
        ),
        "profile": get_profile(),
    }


def database_label() -> str:
    return "Supabase PostgreSQL · persistencia activa"


def database_path() -> str:
    """Backward-compatible label retained for RAC v0.1 code."""
    return database_label()
