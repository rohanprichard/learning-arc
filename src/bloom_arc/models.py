from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    SCHEDULED = "scheduled"
    NEEDS_SCHEDULING = "needs_scheduling"
    PARTIAL_FAILURE = "partial_failure"
    COMPLETED = "completed"


class LearningRequest(BaseModel):
    user_id: str = Field(min_length=1)
    topic: str = Field(min_length=1, max_length=120)
    goal: str = Field(min_length=1, max_length=500)
    availability: str = Field(min_length=1, max_length=500)
    timezone: str = "UTC"


class LessonPlan(BaseModel):
    title: str
    outcome: str
    mastery_items: list[str]
    lesson_markdown: str
    duration_minutes: int = Field(ge=15, le=90)


class LearningRun(BaseModel):
    run_id: str
    idempotency_key: str
    request: LearningRequest
    plan: LessonPlan
    status: RunStatus
    notion_page_id: str | None = None
    notion_url: str | None = None
    calendar_event_id: str | None = None
    calendar_url: str | None = None
    scheduled_start: datetime | None = None
    errors: list[str] = Field(default_factory=list)
    current_lesson: int = 1
    last_reflection: str | None = None


class AgentRun(BaseModel):
    run_id: str
    idempotency_key: str
    status: str
    final_message: str
    duplicate: bool = False
    tool_calls: list[str] = Field(default_factory=list)
