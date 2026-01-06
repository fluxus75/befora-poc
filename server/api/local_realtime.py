import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from server.config import settings
from server.services.local_realtime import LocalRealtimeService, iter_frames

router = APIRouter()


@router.websocket("/api/local-realtime/ws")
async def local_realtime_ws(
    websocket: WebSocket,
    session_id: str,
    sample_rate: int = 16000,
) -> None:
    await websocket.accept()
    try:
        service = LocalRealtimeService(
            model_size=settings.local_stt_model,
            sample_rate=sample_rate,
        )
    except RuntimeError as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
        await websocket.close(code=1011)
        return

    frame_duration_ms = 20
    frame_size = int(sample_rate * 2 * frame_duration_ms / 1000)
    buffer = bytearray()
    speech_buffer = bytearray()
    vad_active = False

    try:
        await websocket.send_json({"type": "status", "state": "connected"})
    except WebSocketDisconnect:
        return

    try:
        while True:
            message: dict[str, Any] = await websocket.receive()
            if "text" in message and message["text"]:
                payload = json.loads(message["text"])
                if payload.get("type") == "stop":
                    break
                continue
            if "bytes" not in message:
                continue
            buffer.extend(message["bytes"])
            for frame in iter_frames(buffer, frame_size):
                is_speech = service.is_speech(frame)
                if is_speech:
                    if not vad_active:
                        vad_active = True
                        await websocket.send_json({"type": "vad", "active": True})
                    speech_buffer.extend(frame)
                    continue
                if vad_active and speech_buffer:
                    vad_active = False
                    await websocket.send_json({"type": "vad", "active": False})
                    text = await service.transcribe_pcm(bytes(speech_buffer))
                    speech_buffer.clear()
                    if text:
                        await websocket.send_json({"type": "transcript", "text": text})
    except WebSocketDisconnect:
        return
    finally:
        if vad_active:
            try:
                await websocket.send_json({"type": "vad", "active": False})
            except WebSocketDisconnect:
                return
