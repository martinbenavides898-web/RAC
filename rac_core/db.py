from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

APP_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = APP_DIR / "data" / "rac.db"
DB_PATH = Path(os.getenv("RAC_DB_PATH", str(DEFAULT_DB_PATH)))


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS shoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                nickname TEXT NOT NULL UNIQUE,
                use_context TEXT NOT NULL DEFAULT '',
                initial_km REAL NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_date TEXT NOT NULL,
                activity_time TEXT,
                activity_type TEXT NOT NULL,
                surface TEXT NOT NULL,
                distance_km REAL NOT NULL,
                duration_min REAL NOT NULL,
                avg_hr INTEGER,
                max_hr INTEGER,
                elevation_gain_m REAL,
                cadence_spm REAL,
                rpe INTEGER NOT NULL,
                pain_before INTEGER NOT NULL,
                pain_during INTEGER NOT NULL,
                pain_after INTEGER NOT NULL,
                pain_location TEXT NOT NULL DEFAULT '',
                shoe_id INTEGER,
                planned_status TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (shoe_id) REFERENCES shoes(id)
            );

            CREATE TABLE IF NOT EXISTS context_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL,
                planned_training INTEGER NOT NULL DEFAULT 0,
                sleep_hours REAL,
                severity INTEGER,
                stress INTEGER,
                study_hours REAL,
                symptoms TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS strength_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL UNIQUE,
                completed INTEGER NOT NULL DEFAULT 0,
                leg_load TEXT NOT NULL DEFAULT 'Ninguna',
                duration_min REAL,
                rpe INTEGER,
                pain_after INTEGER,
                source TEXT NOT NULL DEFAULT 'LagartijApp',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        _seed_shoes(conn)
        _seed_profile(conn)


def _seed_shoes(conn: sqlite3.Connection) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    defaults = [
        ("Brooks", "Ghost 16", "Ghost antiguas", "Universidad y cinta", 252.0, 1, now),
        ("ASICS", "Superblast 2 Tokyo", "Superblast", "Calle, parque, maicillo y fondos", 0.0, 1, now),
    ]
    conn.executemany(
        """
        INSERT OR IGNORE INTO shoes
        (brand, model, nickname, use_context, initial_km, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        defaults,
    )


def _seed_profile(conn: sqlite3.Connection) -> None:
    defaults: dict[str, Any] = {
        "coach_style": "Objetivo, técnico, tranquilo y motivacional sin exagerar",
        "primary_goal": "Correr 10 km como un entrenamiento cotidiano, cómodo y recuperable",
        "endurance_goal": "Completar fondos de más de una hora sin quedar agotado",
        "pace_goal": "Acercar progresivamente el ritmo cómodo a 5:00–4:40 min/km",
        "weekly_plan": {
            "martes": "16:00, cinta, máximo 60 min",
            "miércoles": "16:00, cinta o natación, máximo 60 min",
            "sábado": "08:00, calle/parque/maicillo, hasta 120 min disponibles",
        },
        "injury_history": [
            "Periostitis tibial con episodio punzante 5/10",
            "Dolor lateral de rodilla derecha en enero de 2026, actualmente asintomático",
            "Molestia soportable de tobillos ocasional después de 10 km",
        ],
        "coach_rule": (
            "Reconocer el progreso, pero no transformar una sesión buena en permiso "
            "automático para aumentar mucho la carga."
        ),
    }
    now = datetime.now().isoformat(timespec="seconds")
    for key, value in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO profile (key, value_json, updated_at) VALUES (?, ?, ?)",
            (key, json.dumps(value, ensure_ascii=False), now),
        )


def query(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    with connection() as conn:
        cursor = conn.execute(sql, params)
        return int(cursor.lastrowid or 0)


def get_shoes(active_only: bool = True) -> list[dict[str, Any]]:
    where = "WHERE active = 1" if active_only else ""
    return query(
        f"""
        SELECT s.*,
               s.initial_km + COALESCE(SUM(a.distance_km), 0) AS total_km
        FROM shoes s
        LEFT JOIN activities a ON a.shoe_id = s.id
        {where}
        GROUP BY s.id
        ORDER BY s.active DESC, s.nickname
        """
    )


def add_activity(data: dict[str, Any]) -> int:
    return execute(
        """
        INSERT INTO activities (
            activity_date, activity_time, activity_type, surface,
            distance_km, duration_min, avg_hr, max_hr, elevation_gain_m,
            cadence_spm, rpe, pain_before, pain_during, pain_after,
            pain_location, shoe_id, planned_status, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["activity_date"], data.get("activity_time"), data["activity_type"],
            data["surface"], data["distance_km"], data["duration_min"],
            data.get("avg_hr"), data.get("max_hr"), data.get("elevation_gain_m"),
            data.get("cadence_spm"), data["rpe"], data["pain_before"],
            data["pain_during"], data["pain_after"], data.get("pain_location", ""),
            data.get("shoe_id"), data["planned_status"], data.get("notes", ""),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def add_context_event(data: dict[str, Any]) -> int:
    return execute(
        """
        INSERT INTO context_events (
            event_date, event_type, planned_training, sleep_hours,
            severity, stress, study_hours, symptoms, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["event_date"], data["event_type"], int(data.get("planned_training", False)),
            data.get("sleep_hours"), data.get("severity"), data.get("stress"),
            data.get("study_hours"), data.get("symptoms", ""), data.get("notes", ""),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


def get_profile() -> dict[str, Any]:
    rows = query("SELECT key, value_json FROM profile")
    return {row["key"]: json.loads(row["value_json"]) for row in rows}


def set_profile_value(key: str, value: Any) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO profile (key, value_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at
            """,
            (key, json.dumps(value, ensure_ascii=False), now),
        )


def delete_activity(activity_id: int) -> None:
    execute("DELETE FROM activities WHERE id = ?", (activity_id,))


def database_path() -> Path:
    return DB_PATH
