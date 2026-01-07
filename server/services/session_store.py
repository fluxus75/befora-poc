from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from server.agents.dsl_runner import DSLScenarioRunner
from server.db.database import get_connection
from server.services.encryption import EncryptionService
from shared.schemas.session import (
    SessionCreate,
    SessionDetail,
    SessionListItem,
    SessionListResponse,
    SessionLogEntry,
    SessionNote,
    SessionResponse,
    SessionSlot,
)


@dataclass
class SessionState:
    session: SessionResponse
    runner: DSLScenarioRunner
    turn_index: int = 0


_SESSION_STORE: dict[str, SessionState] = {}

_SCENARIO_PATH = Path(__file__).resolve().parent.parent / "scenarios" / "scenario.json"
_EMERGENCY_KEYWORDS_PATH = (
    Path(__file__).resolve().parent.parent / "scenarios" / "emergency_keywords.json"
)
_EMERGENCY_FLOW_PATH = (
    Path(__file__).resolve().parent.parent / "scenarios" / "EMERGENCY_FLOW.json"
)


def create_session(payload: SessionCreate) -> SessionState:
    patient_id = payload.patient_id
    session_id = str(uuid4())
    created_at = datetime.now(UTC)
    response = SessionResponse(
        session_id=session_id,
        status="active",
        created_at=created_at,
    )
    runner = DSLScenarioRunner(
        _SCENARIO_PATH,
        emergency_keywords_path=_EMERGENCY_KEYWORDS_PATH,
        emergency_flow_path=_EMERGENCY_FLOW_PATH,
    )
    state = SessionState(session=response, runner=runner)
    _SESSION_STORE[session_id] = state
    _insert_session_record(session_id, patient_id, response.status, created_at)
    return state


def get_session(session_id: str) -> SessionState | None:
    return _SESSION_STORE.get(session_id)


def update_session_status(session_id: str, status: str) -> None:
    state = _SESSION_STORE.get(session_id)
    if not state:
        return
    state.session.status = status
    _update_session_status(session_id, status)


def record_session_log(
    session_id: str,
    user_input: str | None,
    agent_response: str | None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO session_logs (session_id, turn_index, user_input, agent_response, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                session_id,
                _next_turn_index(session_id),
                user_input,
                agent_response,
                datetime.now(UTC).isoformat(),
            ),
        )
        connection.commit()


def upsert_session_slots(session_id: str, slots: dict) -> None:
    if not slots:
        return
    encrypted = _encrypt_slots(slots)
    now = datetime.now(UTC).isoformat()
    with get_connection() as connection:
        for slot_key, slot_value in encrypted.items():
            connection.execute(
                "INSERT INTO session_slots (session_id, slot_key, slot_value_encrypted, created_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT(session_id, slot_key) DO UPDATE SET slot_value_encrypted = excluded.slot_value_encrypted",
                (session_id, slot_key, slot_value, now),
            )
        connection.commit()


def list_sessions(
    page: int,
    page_size: int,
    status: str | None = None,
    assigned_doctor_id: str | None = None,
) -> SessionListResponse:
    offset = max(0, (page - 1) * page_size)
    filters = []
    params: list[str] = []
    if status:
        filters.append("status = ?")
        params.append(status)
    if assigned_doctor_id:
        filters.append("assigned_doctor_id = ?")
        params.append(assigned_doctor_id)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    with get_connection() as connection:
        total_cursor = connection.execute(
            f"SELECT COUNT(*) as count FROM sessions {where_clause}",
            params,
        )
        total = int(total_cursor.fetchone()["count"])
        cursor = connection.execute(
            f"""
            SELECT id, status, created_at, completed_at, assigned_doctor_id, reviewed_at, confirmed_at
            FROM sessions
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (*params, page_size, offset),
        )
        items = [
            SessionListItem(**_row_to_session_list_item(row))
            for row in cursor.fetchall()
        ]
    return SessionListResponse(items=items, total=total, page=page, page_size=page_size)


def get_session_detail(session_id: str) -> SessionDetail | None:
    with get_connection() as connection:
        session_row = connection.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if not session_row:
            return None
        slot_rows = connection.execute(
            "SELECT slot_key, slot_value_encrypted FROM session_slots WHERE session_id = ?",
            (session_id,),
        ).fetchall()
        log_rows = connection.execute(
            "SELECT turn_index, user_input, agent_response, timestamp FROM session_logs "
            "WHERE session_id = ? ORDER BY turn_index",
            (session_id,),
        ).fetchall()
        note_rows = connection.execute(
            "SELECT id, doctor_id, note, created_at FROM session_notes "
            "WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        ).fetchall()
    patient_id = _decrypt_value(session_row["patient_id_encrypted"])
    slots = [
        SessionSlot(
            slot_key=row["slot_key"],
            slot_value=_decrypt_value(row["slot_value_encrypted"]),
        )
        for row in slot_rows
    ]
    logs = [
        SessionLogEntry(
            turn_index=row["turn_index"],
            user_input=row["user_input"],
            agent_response=row["agent_response"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )
        for row in log_rows
    ]
    notes = [
        SessionNote(
            id=row["id"],
            doctor_id=row["doctor_id"],
            note=row["note"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in note_rows
    ]
    return SessionDetail(
        session_id=session_row["id"],
        status=session_row["status"],
        created_at=datetime.fromisoformat(session_row["created_at"]),
        completed_at=_parse_optional_dt(session_row["completed_at"]),
        assigned_doctor_id=session_row["assigned_doctor_id"],
        reviewed_at=_parse_optional_dt(session_row["reviewed_at"]),
        confirmed_at=_parse_optional_dt(session_row["confirmed_at"]),
        patient_id=patient_id,
        slots=slots,
        logs=logs,
        notes=notes,
    )


def add_session_note(session_id: str, doctor_id: str, note: str) -> SessionNote:
    now = datetime.now(UTC).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO session_notes (session_id, doctor_id, note, created_at) "
            "VALUES (?, ?, ?, ?)",
            (session_id, doctor_id, note, now),
        )
        connection.commit()
        note_id = cursor.lastrowid
    return SessionNote(
        id=int(note_id),
        doctor_id=doctor_id,
        note=note,
        created_at=datetime.fromisoformat(now),
    )


def update_session_assignment(session_id: str, doctor_id: str | None) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE sessions SET assigned_doctor_id = ? WHERE id = ?",
            (doctor_id, session_id),
        )
        connection.commit()


def set_session_status(session_id: str, status: str) -> None:
    timestamp = datetime.now(UTC).isoformat()
    updates: dict[str, str] = {}
    if status == "completed":
        updates["completed_at"] = timestamp
    if status == "reviewed":
        updates["reviewed_at"] = timestamp
    if status == "confirmed":
        updates["confirmed_at"] = timestamp
    with get_connection() as connection:
        if updates:
            assignments = ", ".join([f"{key} = ?" for key in updates])
            params = (status, *updates.values(), session_id)
            connection.execute(
                f"UPDATE sessions SET status = ?, {assignments} WHERE id = ?",
                params,
            )
        else:
            connection.execute(
                "UPDATE sessions SET status = ? WHERE id = ?",
                (status, session_id),
            )
        connection.commit()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _parse_optional_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _row_to_session_list_item(row) -> dict:
    return {
        "session_id": row["id"],
        "status": row["status"],
        "created_at": datetime.fromisoformat(row["created_at"]),
        "completed_at": _parse_optional_dt(row["completed_at"]),
        "assigned_doctor_id": row["assigned_doctor_id"],
        "reviewed_at": _parse_optional_dt(row["reviewed_at"]),
        "confirmed_at": _parse_optional_dt(row["confirmed_at"]),
    }


def _get_encryption_service() -> EncryptionService:
    if not hasattr(_get_encryption_service, "_cached"):
        _get_encryption_service._cached = EncryptionService()  # type: ignore[attr-defined]
    return _get_encryption_service._cached  # type: ignore[attr-defined]


def _encrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    return _get_encryption_service().encrypt(value)


def _decrypt_value(value: str | None) -> str | None:
    if value is None:
        return None
    return _get_encryption_service().decrypt(value)


def _normalize_slot_value(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=True)


def _encrypt_slots(slots: dict) -> dict[str, str | None]:
    encrypted: dict[str, str | None] = {}
    for key, value in slots.items():
        normalized = _normalize_slot_value(value)
        encrypted[key] = _encrypt_value(normalized)
    return encrypted


def _next_turn_index(session_id: str) -> int:
    state = _SESSION_STORE.get(session_id)
    if not state:
        return 0
    state.turn_index += 1
    return state.turn_index


def _insert_session_record(
    session_id: str,
    patient_id: str | None,
    status: str,
    created_at: datetime,
) -> None:
    encrypted_patient_id = _encrypt_value(patient_id) if patient_id else None
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO sessions (id, patient_id_encrypted, status, created_at) "
            "VALUES (?, ?, ?, ?)",
            (session_id, encrypted_patient_id, status, created_at.isoformat()),
        )
        connection.commit()


def _update_session_status(session_id: str, status: str) -> None:
    timestamp = _now_iso()
    update_fields = {"status": status}
    if status == "completed":
        update_fields["completed_at"] = timestamp
    if status == "emergency_terminated":
        update_fields["completed_at"] = timestamp
    assignments = ", ".join([f"{key} = ?" for key in update_fields])
    values = list(update_fields.values()) + [session_id]
    with get_connection() as connection:
        connection.execute(
            f"UPDATE sessions SET {assignments} WHERE id = ?",
            values,
        )
        connection.commit()
