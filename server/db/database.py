from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from server.db.models import (
    AUTH_SESSIONS_TABLE,
    LOGS_TABLE,
    NOTES_TABLE,
    SESSIONS_TABLE,
    SLOT_TABLE,
    USERS_TABLE,
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./befora.db")


def _sqlite_path_from_url(url: str) -> Path:
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this PoC")
    return Path(url.replace("sqlite:///", "", 1)).resolve()


def get_connection() -> sqlite3.Connection:
    db_path = _sqlite_path_from_url(DATABASE_URL)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db() -> None:
    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(USERS_TABLE)
        connection.execute(SESSIONS_TABLE)
        connection.execute(SLOT_TABLE)
        connection.execute(LOGS_TABLE)
        connection.execute(NOTES_TABLE)
        connection.execute(AUTH_SESSIONS_TABLE)
        connection.commit()
