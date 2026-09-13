from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .models import LearningRequest, LearningRun, LessonPlan


class BloomPlanner(Protocol):
    def create_first_lesson(self, request: LearningRequest) -> LessonPlan: ...

    def create_next_lesson(self, run: LearningRun, reflection: str) -> LessonPlan: ...


class AppGateway(Protocol):
    def create_notion_page(self, request: LearningRequest, plan: LessonPlan) -> tuple[str, str]: ...

    def find_free_slot(self, request: LearningRequest, duration_minutes: int) -> datetime | None: ...

    def create_calendar_event(
        self, request: LearningRequest, plan: LessonPlan, start: datetime
    ) -> tuple[str, str]: ...

    def update_notion_page(self, page_id: str, plan: LessonPlan) -> None: ...


class RunStore(Protocol):
    def get_by_idempotency_key(self, key: str) -> LearningRun | None: ...

    def save(self, run: LearningRun) -> None: ...

    def get_by_run_id(self, run_id: str) -> LearningRun | None: ...
