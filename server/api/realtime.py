from fastapi import APIRouter, HTTPException

from server.auth.token import EphemeralTokenError, create_ephemeral_token
from server.services.session_store import get_session as get_session_state
from shared.schemas.realtime import EphemeralTokenRequest, EphemeralTokenResponse

router = APIRouter()


@router.post("/api/realtime/token", response_model=EphemeralTokenResponse)
def issue_ephemeral_token(payload: EphemeralTokenRequest) -> EphemeralTokenResponse:
    """Issue an ephemeral token for Realtime WebRTC connection."""
    state = get_session_state(payload.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        token_result = create_ephemeral_token(payload.session_id)
    except EphemeralTokenError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return EphemeralTokenResponse(
        token=token_result.token,
        expires_in=token_result.expires_in,
    )
