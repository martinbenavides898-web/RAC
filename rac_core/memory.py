from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from typing import Any

from rac_core.db import (
    get_activities,
    get_context_events,
    get_memories,
    get_profile,
)

PROMPT_VERSION = "rac-coach-2026-07-v1"


def _compact_activity(activity: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": activity.get("id"),
        "date": activity.get("activity_date"),
        "time": activity.get("activity_time"),
        "type": activity.get("activity_type"),
        "surface": activity.get("surface"),
        "distance_km": activity.get("distance_km"),
        "duration_min": activity.get("duration_min"),
        "avg_hr": activity.get("avg_hr"),
        "max_hr": activity.get("max_hr"),
        "elevation_gain_m": activity.get("elevation_gain_m"),
        "cadence_spm": activity.get("cadence_spm"),
        "rpe": activity.get("rpe"),
        "pain_before": activity.get("pain_before"),
        "pain_during": activity.get("pain_during"),
        "pain_after": activity.get("pain_after"),
        "pain_location": activity.get("pain_location"),
        "shoe": activity.get("shoe_name"),
        "planned_status": activity.get("planned_status"),
        "notes": activity.get("notes"),
    }


def _compact_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": event.get("event_date"),
        "type": event.get("event_type"),
        "planned_training": event.get("planned_training"),
        "sleep_hours": event.get("sleep_hours"),
        "severity": event.get("severity"),
        "stress": event.get("stress"),
        "study_hours": event.get("study_hours"),
        "symptoms": event.get("symptoms"),
        "notes": event.get("notes"),
    }


def build_context(
    *,
    task: str,
    target_activity: dict[str, Any] | None = None,
    period_start: str | None = None,
    period_end: str | None = None,
    question: str = "",
) -> dict[str, Any]:
    profile = get_profile()
    policy = profile.get("memory_policy") or {}
    recent_days = int(policy.get("recent_activity_days", 14))
    today = date.today()
    recent_start = (today - timedelta(days=recent_days - 1)).isoformat()
    recent_end = today.isoformat()

    recent_activities = get_activities(recent_start, recent_end, descending=False)
    recent_events = get_context_events(recent_start, recent_end, descending=False)

    period_activities: list[dict[str, Any]] = []
    period_events: list[dict[str, Any]] = []
    if period_start and period_end:
        period_activities = get_activities(period_start, period_end, descending=False)
        period_events = get_context_events(period_start, period_end, descending=False)

    memories = get_memories(active_only=True, limit=20)

    return {
        "task": task,
        "question": question.strip(),
        "today": today.isoformat(),
        "profile": {
            "coach_style": profile.get("coach_style"),
            "primary_goal": profile.get("primary_goal"),
            "endurance_goal": profile.get("endurance_goal"),
            "pace_goal": profile.get("pace_goal"),
            "coach_rule": profile.get("coach_rule"),
            "runner_profile": profile.get("runner_profile"),
            "availability_profile": profile.get("availability_profile"),
            "communication_profile": profile.get("communication_profile"),
        },
        "selected_memories": [
            {
                "category": m["category"],
                "title": m["title"],
                "content": m["content"],
                "importance": m["importance"],
            }
            for m in memories
        ],
        "target_activity": _compact_activity(target_activity) if target_activity else None,
        "period": {
            "start": period_start,
            "end": period_end,
            "activities": [_compact_activity(a) for a in period_activities],
            "context_events": [_compact_event(e) for e in period_events],
        },
        "recent_14_days": {
            "activities": [_compact_activity(a) for a in recent_activities],
            "context_events": [_compact_event(e) for e in recent_events],
        },
    }


def context_hash(context: dict[str, Any]) -> str:
    canonical = json.dumps(context, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256((PROMPT_VERSION + canonical).encode("utf-8")).hexdigest()


def context_size(context: dict[str, Any]) -> int:
    return len(json.dumps(context, ensure_ascii=False, default=str))
