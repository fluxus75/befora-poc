from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./befora.db")


def _sqlite_path_from_url(url: str) -> Path:
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this PoC")
    return Path(url.replace("sqlite:///", "", 1)).resolve()


def get_connection() -> sqlite3.Connection:
    db_path = _sqlite_path_from_url(DATABASE_URL)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)
