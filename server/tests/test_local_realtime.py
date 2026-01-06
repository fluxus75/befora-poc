import pytest
from fastapi.testclient import TestClient

from server.main import app


class FakeLocalRealtimeService:
    def __init__(self, model_size: str, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        self.calls = 0

    def is_speech(self, frame: bytes) -> bool:
        self.calls += 1
        return self.calls == 1

    async def transcribe_pcm(self, pcm_bytes: bytes) -> str:
        return "안녕하세요"


def test_local_realtime_ws_framing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "server.api.local_realtime.LocalRealtimeService", FakeLocalRealtimeService
    )
    client = TestClient(app)
    frame_size = 640  # 20ms @ 16kHz, 16-bit mono
    payload = b"\x01\x00" * (frame_size)

    with client.websocket_connect("/api/local-realtime/ws?session_id=demo") as ws:
        status = ws.receive_json()
        assert status["type"] == "status"

        ws.send_bytes(payload * 2)
        vad_start = ws.receive_json()
        vad_stop = ws.receive_json()
        transcript = ws.receive_json()

        assert vad_start == {"type": "vad", "active": True}
        assert vad_stop == {"type": "vad", "active": False}
        assert transcript == {"type": "transcript", "text": "안녕하세요"}

        ws.send_json({"type": "stop"})
