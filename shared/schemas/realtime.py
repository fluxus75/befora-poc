from typing import Any

from pydantic import BaseModel, Field


class EphemeralTokenRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from /api/sessions")


class EphemeralTokenResponse(BaseModel):
    token: str
    expires_in: int = Field(..., description="Token lifetime in seconds")


class AudioMetadata(BaseModel):
    duration_ms: int | None = None
    transcript_confidence: float | None = None
    volume: float | None = None


class ProcessTurnRequest(BaseModel):
    user_input: str
    audio_metadata: AudioMetadata | None = None


class ProcessTurnResponse(BaseModel):
    agent_response: str
    current_node: str
    completed: bool
    emergency: bool
    slots: dict[str, Any]
