from __future__ import annotations

import asyncio
from collections.abc import Iterable


class LocalRealtimeService:
    """Local STT service backed by faster-whisper + webrtcvad."""

    def __init__(self, model_size: str, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        try:
            import webrtcvad
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - runtime guard
            raise RuntimeError(
                "Local realtime dependencies missing. Install with: "
                'uv pip install -e ".[local-realtime]"'
            ) from exc

        self.whisper = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )
        self.vad = webrtcvad.Vad(mode=3)

    def is_speech(self, frame: bytes) -> bool:
        return self.vad.is_speech(frame, self.sample_rate)

    async def transcribe_pcm(self, pcm_bytes: bytes) -> str:
        if not pcm_bytes:
            return ""
        audio = await asyncio.to_thread(self._pcm_to_float32, pcm_bytes)
        return await asyncio.to_thread(self._transcribe_audio, audio)

    def _transcribe_audio(self, audio: object) -> str:
        segments, _info = self.whisper.transcribe(
            audio,
            language="ko",
            beam_size=1,
            vad_filter=True,
        )
        parts = [segment.text.strip() for segment in segments]
        return " ".join(part for part in parts if part).strip()

    @staticmethod
    def _pcm_to_float32(pcm_bytes: bytes) -> object:
        try:
            import numpy as np
        except ImportError as exc:  # pragma: no cover - runtime guard
            raise RuntimeError(
                "Local realtime dependencies missing. Install with: "
                'uv pip install -e ".[local-realtime]"'
            ) from exc
        return np.frombuffer(pcm_bytes, np.int16).astype("float32") / 32768.0


def iter_frames(buffer: bytearray, frame_size: int) -> Iterable[bytes]:
    while len(buffer) >= frame_size:
        frame = bytes(buffer[:frame_size])
        del buffer[:frame_size]
        yield frame
