"""
Configuration module for Befora POC.

Loads environment variables and provides typed configuration objects.
"""

import os
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
        "alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"
    ] = Field(
        default="alloy", validation_alias="REALTIME_VOICE"
    )
    realtime_temperature: float = Field(
        default=0.8, ge=0.0, le=2.0, validation_alias="REALTIME_TEMPERATURE"
    )
    realtime_max_tokens: int = Field(
        default=4096, ge=1, le=16384, validation_alias="REALTIME_MAX_TOKENS"
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
