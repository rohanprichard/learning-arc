from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    bloom_arc_mode: str = "mock"
    bloom_arc_user_id: str = "demo-user"
    agent_model: str = "openrouter:deepseek/deepseek-v4.1-flash"
    enable_google_tasks: bool = False
    openai_model: str = "gpt-5-mini"
    notion_parent_page_id: str = ""
    availability_start: str = "2026-09-15T18:00:00+05:30"
    availability_end: str = "2026-09-15T22:00:00+05:30"
