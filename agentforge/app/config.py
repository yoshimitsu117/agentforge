"""AgentForge — Configuration & Settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    app_name: str = "AgentForge"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = "gpt-4o-mini"
    temperature: float = 0.1

    # Workflow
    max_iterations: int = 15
    recursion_limit: int = 25

    # Memory
    memory_backend: str = "in_memory"  # in_memory or sqlite

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
