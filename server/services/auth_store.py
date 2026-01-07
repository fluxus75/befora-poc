from __future__ import annotations

import base64
import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from server.db.database import get_connection

_SESSION_EXPIRY_HOURS = 8


@dataclass
class AuthSession:
    user_id: str
    csrf_token: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _parse_password_hash(stored: str) -> tuple[int, bytes, bytes]:
    algorithm, iterations, salt_b64, hash_b64 = stored.split("$", maxsplit=3)
    if algorithm != "pbkdf2_sha256":
        raise ValueError("Unsupported password hash algorithm")
    return int(iterations), base64.b64decode(salt_b64), base64.b64decode(hash_b64)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    iterations = 120_000
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.b64encode(salt).decode("utf-8"),
        base64.b64encode(hashed).decode("utf-8"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    iterations, salt, expected = _parse_password_hash(stored_hash)
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return secrets.compare_digest(candidate, expected)


def ensure_default_users() -> None:
    default_password = os.getenv("DASHBOARD_DEFAULT_PASSWORD", "password")
    with get_connection() as connection:
        cursor = connection.execute("SELECT COUNT(*) as count FROM users")
        count = int(cursor.fetchone()["count"])
        if count > 0:
            return
        now = _now_iso()
        users = [
            (str(uuid4()), "admin", hash_password(default_password), "admin", now),
            (str(uuid4()), "doctor", hash_password(default_password), "doctor", now),
            (
                str(uuid4()),
                "reviewer",
                hash_password(default_password),
                "reviewer",
                now,
            ),
        ]
        connection.executemany(
            "INSERT INTO users (id, username, password_hash, role, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            users,
        )
        connection.commit()


def get_user_by_username(username: str) -> dict | None:
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> dict | None:
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT id, username, role FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def create_auth_session(user_id: str) -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(hours=_SESSION_EXPIRY_HOURS)
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO auth_sessions (session_token, user_id, csrf_token, expires_at) "
            "VALUES (?, ?, ?, ?)",
            (token, user_id, csrf_token, expires_at.isoformat()),
        )
        connection.commit()
    return token, csrf_token


def get_auth_session(token: str) -> AuthSession | None:
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT user_id, csrf_token, expires_at FROM auth_sessions "
            "WHERE session_token = ?",
            (token,),
        )
        row = cursor.fetchone()
    if not row:
        return None
    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at < datetime.now(UTC):
        delete_auth_session(token)
        return None
    return AuthSession(user_id=row["user_id"], csrf_token=row["csrf_token"])


def delete_auth_session(token: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM auth_sessions WHERE session_token = ?",
            (token,),
        )
        connection.commit()
