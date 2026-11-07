"""Validated deployment settings. No configuration secrets are logged."""

import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    version: str = "1.0.0"
    session_seconds: int = Field(default=3600, ge=60, le=86400)
    requests_per_minute: int = Field(default=240, ge=10, le=10000)
    retention_days: int = Field(default=90, ge=1, le=3650)
    max_batch: int = Field(default=1000, ge=1, le=10000)


def settings():
    return Settings(
        **{
            key: os.environ["SENTINEL_" + key.upper()]
            for key in Settings.model_fields
            if "SENTINEL_" + key.upper() in os.environ
        }
    )
