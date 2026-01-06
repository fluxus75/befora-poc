from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from shared.schemas.session import SessionCreate, SessionResponse

from server.agents.dsl_runner import DSLScenarioRunner


@dataclass
class SessionState:
    session: SessionResponse
    runner: DSLScenarioRunner


_SESSION_STORE: dict[str, SessionState] = {}

_SCENARIO_PATH = Path(__file__).resolve().parent.parent / "scenarios" / "scenario.json"
_EMERGENCY_KEYWORDS_PATH = (
    Path(__file__).resolve().parent.parent / "scenarios" / "emergency_keywords.json"
)
_EMERGENCY_FLOW_PATH = (
    Path(__file__).resolve().parent.parent / "scenarios" / "EMERGENCY_FLOW.json"
)


def create_session(payload: SessionCreate) -> SessionState:
    _ = payload
    session_id = str(uuid4())
    response = SessionResponse(
        session_id=session_id,
        status="active",
        created_at=datetime.now(timezone.utc),
    )
    runner = DSLScenarioRunner(
        _SCENARIO_PATH,
        emergency_keywords_path=_EMERGENCY_KEYWORDS_PATH,
        emergency_flow_path=_EMERGENCY_FLOW_PATH,
    )
    state = SessionState(session=response, runner=runner)
    _SESSION_STORE[session_id] = state
    return state


def get_session(session_id: str) -> SessionState | None:
    return _SESSION_STORE.get(session_id)


def update_session_status(session_id: str, status: str) -> None:
    state = _SESSION_STORE.get(session_id)
    if not state:
        return
    state.session.status = status
