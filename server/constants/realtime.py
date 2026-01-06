"""
OpenAI Realtime API constants and configurations.

Reference: https://platform.openai.com/docs/guides/realtime
"""

from typing import Literal

# Available Realtime Models (as of 2025-01)
# Reference: https://platform.openai.com/docs/models/gpt-realtime
REALTIME_MODELS = [
    "gpt-realtime",  # GA model (recommended, 20% cheaper than preview)
    "gpt-4o-mini-realtime-preview",  # Low-cost alternative
    "gpt-4o-realtime-preview-2024-12-17",  # Legacy preview version
]

# Available Voice Options (10 voices as of 2025-01)
# Reference: https://platform.openai.com/docs/guides/realtime
RealtimeVoice = Literal[
    "alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"
]

VOICE_DESCRIPTIONS = {
    "alloy": "Neutral, balanced voice (recommended for medical interviews)",
    "ash": "Clear, precise voice",
    "ballad": "Melodic, smooth voice",
    "coral": "Warm, friendly voice",
    "echo": "Resonant, deep voice",
    "sage": "Calm, thoughtful voice (good for medical context)",
    "shimmer": "Bright, energetic voice",
    "verse": "Versatile, expressive voice",
    "marin": "Professional, clear voice",
    "cedar": "Authoritative, confident voice",
}

# Audio Configuration
AUDIO_FORMAT = "pcm16"  # 16-bit PCM
SAMPLE_RATE = 24000  # 24kHz (OpenAI Realtime default)

# Turn Detection (VAD - Voice Activity Detection)
TURN_DETECTION_CONFIG = {
    "type": "server_vad",
    "threshold": 0.5,  # 0.0 (sensitive) - 1.0 (conservative)
    "prefix_padding_ms": 300,  # Padding before speech
    "silence_duration_ms": 500,  # Silence to detect turn end
}

# Session Configuration (for gpt-realtime model)
# Reference: https://platform.openai.com/docs/api-reference/realtime
SESSION_CONFIG = {
    "model": "gpt-realtime",  # Will be overridden by settings
    "modalities": ["text", "audio"],  # Enable both text and audio
    "instructions": """You are a compassionate medical assistant conducting a pre-appointment interview.
Speak clearly and naturally in Korean. Ask one question at a time.
If the patient mentions emergency symptoms, immediately alert them to seek urgent care.""",
    "voice": "alloy",  # Will be overridden by settings
    "input_audio_format": AUDIO_FORMAT,
    "output_audio_format": AUDIO_FORMAT,
    "input_audio_transcription": {
        "model": "whisper-1",
    },
    "turn_detection": TURN_DETECTION_CONFIG,
    "temperature": 0.8,  # Will be overridden by settings
    "max_response_output_tokens": 4096,  # Will be overridden by settings
}

# WebRTC Configuration
WEBRTC_CONFIG = {
    "iceServers": [
        {"urls": "stun:stun.l.google.com:19302"},
        # Add TURN servers here if needed for production
    ],
}

# Connection Settings
CONNECTION_TIMEOUT_MS = 10000  # 10 seconds
RECONNECT_MAX_RETRIES = 5
RECONNECT_BASE_DELAY_MS = 1000
RECONNECT_MAX_DELAY_MS = 16000
RECONNECT_BACKOFF_MULTIPLIER = 2

# Session Restore Settings
SESSION_RESTORE_TIMEOUT_SECONDS = 30
