from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserRecord:
    id: str
    username: str
    password_hash: str
    role: str
    created_at: datetime


@dataclass
class SessionRecord:
    id: str
    patient_id_encrypted: str | None
    status: str
    created_at: datetime
    completed_at: datetime | None
    assigned_doctor_id: str | None
    reviewed_at: datetime | None
    confirmed_at: datetime | None


@dataclass
class SessionSlotRecord:
    session_id: str
    slot_key: str
    slot_value_encrypted: str | None
    created_at: datetime


@dataclass
class SessionLogRecord:
    session_id: str
    turn_index: int
    user_input: str | None
    agent_response: str | None
    timestamp: datetime


@dataclass
class SessionNoteRecord:
    id: int
    session_id: str
    doctor_id: str
    note: str
    created_at: datetime


@dataclass
class AuthSessionRecord:
    session_token: str
    user_id: str
    csrf_token: str
    expires_at: datetime


USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'reviewer')),
    created_at TEXT NOT NULL
);
"""

SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    patient_id_encrypted TEXT,
    status TEXT NOT NULL CHECK(
        status IN ('active', 'completed', 'emergency_terminated', 'reviewed', 'confirmed')
    ),
    created_at TEXT NOT NULL,
    completed_at TEXT,
    assigned_doctor_id TEXT REFERENCES users(id),
    reviewed_at TEXT,
    confirmed_at TEXT
);
"""

SLOT_TABLE = """
CREATE TABLE IF NOT EXISTS session_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
    slot_key TEXT NOT NULL,
    slot_value_encrypted TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(session_id, slot_key)
);
"""

LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
    turn_index INTEGER NOT NULL,
    user_input TEXT,
    agent_response TEXT,
    timestamp TEXT NOT NULL
);
"""

NOTES_TABLE = """
CREATE TABLE IF NOT EXISTS session_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
    doctor_id TEXT REFERENCES users(id),
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

AUTH_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS auth_sessions (
    session_token TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    csrf_token TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
"""
