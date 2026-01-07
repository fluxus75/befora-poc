"""
Configuration module for Befora POC.

Loads environment variables and provides typed configuration objects.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI API Configuration
    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    openai_org_id: str | None = Field(None, validation_alias="OPENAI_ORG_ID")
    openai_project_id: str | None = Field(None, validation_alias="OPENAI_PROJECT_ID")

    # Realtime API Settings
    realtime_model: str = Field(
        default="gpt-realtime",
        validation_alias="REALTIME_MODEL",
    )
    realtime_voice: Literal[
        "alloy",
        "ash",
        "ballad",
        "coral",
        "echo",
        "sage",
        "shimmer",
        "verse",
        "marin",
        "cedar",
    ] = Field(default="alloy", validation_alias="REALTIME_VOICE")
    realtime_temperature: float = Field(
        default=0.8, ge=0.0, le=2.0, validation_alias="REALTIME_TEMPERATURE"
    )
    realtime_max_tokens: int = Field(
        default=4096, ge=1, le=16384, validation_alias="REALTIME_MAX_TOKENS"
    )
    realtime_provider: Literal["openai", "mock", "local"] = Field(
        default="openai", validation_alias="REALTIME_PROVIDER"
    )
    mock_scenario_path: str = Field(
        default="server/fixtures/mock_transcripts.json",
        validation_alias="MOCK_SCENARIO_PATH",
    )
    mock_latency_ms: int = Field(default=500, ge=0, validation_alias="MOCK_LATENCY_MS")
    local_stt_model: str = Field(default="base", validation_alias="LOCAL_STT_MODEL")
    local_tts_engine: Literal["browser", "coqui", "piper"] = Field(
        default="browser", validation_alias="LOCAL_TTS_ENGINE"
    )
    local_llm_endpoint: str | None = Field(
        default=None, validation_alias="LOCAL_LLM_ENDPOINT"
    )

    # Ephemeral Token Settings
    ephemeral_token_expire_seconds: int = Field(
        default=60, ge=30, le=300, validation_alias="EPHEMERAL_TOKEN_EXPIRE_SECONDS"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./befora.db", validation_alias="DATABASE_URL"
    )

    # General
    debug: bool = Field(default=False, validation_alias="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
