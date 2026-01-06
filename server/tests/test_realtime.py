import io
import json
import time
from urllib.error import HTTPError

import pytest
from fastapi.testclient import TestClient

from server.auth import token as token_module
from server.auth.token import _build_session_payload
from server.config import settings
from server.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_session_payload_schema_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "realtime_model", "gpt-realtime")
    monkeypatch.setattr(settings, "realtime_voice", "alloy")
    monkeypatch.setattr(settings, "realtime_temperature", 0.7)
    monkeypatch.setattr(settings, "realtime_max_tokens", 1024)

    payload = _build_session_payload("session-123")
    required_keys = {
        "model",
        "modalities",
        "instructions",
        "voice",
        "input_audio_transcription",
        "turn_detection",
    }

    assert required_keys.issubset(payload.keys())
    assert payload["model"] == "gpt-realtime"
    assert payload["voice"] == "alloy"


def test_issue_ephemeral_token_success(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    session_id = client.post("/api/sessions", json={}).json()["session_id"]

    expires_at = int(time.time()) + 60
    response_body = json.dumps(
        {"client_secret": {"value": "eph_test_token", "expires_at": expires_at}}
    ).encode("utf-8")

    class _FakeResponse:
        def __enter__(self) -> "_FakeResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def read(self) -> bytes:
            return response_body

    def fake_urlopen(request, timeout=10):  # noqa: ANN001 - signature match
        return _FakeResponse()

    monkeypatch.setattr(token_module, "urlopen", fake_urlopen)

    response = client.post("/api/realtime/token", json={"session_id": session_id})
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"token", "expires_in"}
    assert data["token"] == "eph_test_token"


def test_issue_ephemeral_token_error(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    session_id = client.post("/api/sessions", json={}).json()["session_id"]
    fp = io.BytesIO(b'{"error":"bad request"}')
    error = HTTPError(
        url="https://api.openai.com/v1/realtime/sessions",
        code=400,
        msg="Bad Request",
        hdrs=None,
        fp=fp,
    )

    def fake_urlopen(request, timeout=10):  # noqa: ANN001 - signature match
        raise error

    monkeypatch.setattr(token_module, "urlopen", fake_urlopen)
    response = client.post("/api/realtime/token", json={"session_id": session_id})
    assert response.status_code == 502


def test_process_turn_contract(client: TestClient) -> None:
    session_id = client.post("/api/sessions", json={}).json()["session_id"]
    response = client.post(
        f"/api/sessions/{session_id}/process", json={"user_input": "네, 동의합니다"}
    )
    assert response.status_code == 200
    data = response.json()
    expected_keys = {
        "agent_response",
        "current_node",
        "completed",
        "emergency",
        "slots",
    }
    assert expected_keys.issubset(data.keys())
