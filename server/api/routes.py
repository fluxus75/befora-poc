import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from server import __version__
from server.config import settings
from server.services.session_store import (
    create_session as create_session_state,
    get_session as get_session_state,
    update_session_status,
)
from shared.schemas.health import HealthResponse
from shared.schemas.realtime import ProcessTurnRequest, ProcessTurnResponse
from shared.schemas.session import SessionCreate, SessionResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint for monitoring and load balancer."""
    return HealthResponse(
        status="ok",
        version=__version__,
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/api/sessions", response_model=SessionResponse)
def create_session(payload: SessionCreate) -> SessionResponse:
    """Create a new voice session."""
    state = create_session_state(payload)
    return state.session


@router.get("/api/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    """Get session by ID."""
    state = get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return state.session


@router.post(
    "/api/sessions/{session_id}/process",
    response_model=ProcessTurnResponse,
)
def process_turn(
    session_id: str,
    payload: ProcessTurnRequest,
) -> ProcessTurnResponse:
    """Process a single user turn via the DSL engine."""
    state = get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    response = state.runner.process(payload.user_input)
    if response.is_emergency:
        update_session_status(session_id, "emergency")
    elif response.is_complete:
        update_session_status(session_id, "completed")
    return ProcessTurnResponse(
        agent_response=response.text,
        current_node=response.current_node,
        completed=response.is_complete,
        emergency=response.is_emergency,
        slots=response.slots,
    )


@router.get("/api/mock-scenarios")
def get_mock_scenarios() -> JSONResponse:
    """Return mock transcripts for the realtime mock provider."""
    path = Path(settings.mock_scenario_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Mock scenario not found")
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return JSONResponse(content=data)
