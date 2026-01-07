from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from server.config import settings
from server.constants.api_endpoints import REALTIME_SESSION_ENDPOINT
from server.constants.realtime import (
    SESSION_CONFIG,
    TURN_DETECTION_CONFIG,
)


@dataclass
class EphemeralTokenResult:
    token: str
    expires_in: int
    expires_at: int


class EphemeralTokenError(RuntimeError):
    pass


def _build_session_payload(session_id: str) -> dict[str, Any]:
    return {
        "model": settings.realtime_model,
        "voice": settings.realtime_voice,
        "modalities": SESSION_CONFIG.get("modalities", ["audio", "text"]),
        "instructions": SESSION_CONFIG.get("instructions", ""),
        "input_audio_transcription": SESSION_CONFIG.get(
            "input_audio_transcription", {"model": "whisper-1"}
        ),
        "turn_detection": TURN_DETECTION_CONFIG,
    }


def create_ephemeral_token(session_id: str) -> EphemeralTokenResult:
    payload = _build_session_payload(session_id)
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "realtime=v1",
    }
    if settings.openai_org_id:
        headers["OpenAI-Organization"] = settings.openai_org_id
    if settings.openai_project_id:
        headers["OpenAI-Project"] = settings.openai_project_id

    request = Request(
        REALTIME_SESSION_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8") if exc.fp else str(exc)
        raise EphemeralTokenError(f"OpenAI error: {detail}") from exc
    except URLError as exc:
        raise EphemeralTokenError(f"Network error: {exc}") from exc

    data = json.loads(body)
    client_secret = data.get("client_secret") or {}
    token = client_secret.get("value")
    expires_at = int(client_secret.get("expires_at", 0))
    if not token:
        raise EphemeralTokenError("OpenAI response missing client_secret.value")

    now = int(time.time())
    expires_in = max(0, expires_at - now)
    return EphemeralTokenResult(
        token=token,
        expires_in=expires_in or settings.ephemeral_token_expire_seconds,
        expires_at=expires_at or (now + settings.ephemeral_token_expire_seconds),
    )
