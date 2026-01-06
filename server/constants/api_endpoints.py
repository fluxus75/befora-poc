"""
OpenAI API endpoints for Realtime API.

Reference: https://platform.openai.com/docs/api-reference/realtime
"""

# Base URL
OPENAI_API_BASE = "https://api.openai.com/v1"

# Realtime API Endpoints (as of 2025-01)
REALTIME_WEBSOCKET_URL = "wss://api.openai.com/v1/realtime"
REALTIME_WEBRTC_ENDPOINT = f"{OPENAI_API_BASE}/realtime/calls"
REALTIME_SESSION_ENDPOINT = f"{OPENAI_API_BASE}/realtime/sessions"

# API Version
API_VERSION = "2025-08-28"  # Latest API version for Realtime


def get_websocket_url(model: str = "gpt-realtime") -> str:
    """
    Get WebSocket URL for Realtime API connection.

    Args:
        model: Model name (default: gpt-realtime)

    Returns:
        WebSocket URL with model parameter
    """
    return f"{REALTIME_WEBSOCKET_URL}?model={model}"


def get_webrtc_endpoint() -> str:
    """
    Get WebRTC endpoint for creating Realtime API calls.

    Returns:
        POST endpoint URL for WebRTC session creation
    """
    return REALTIME_WEBRTC_ENDPOINT
