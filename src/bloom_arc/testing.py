from __future__ import annotations

from datetime import datetime

from .models import LearningRequest, LearningRun, LessonPlan


class StaticBloomPlanner:
    def create_first_lesson(self, request: LearningRequest) -> LessonPlan:
        return LessonPlan(
            title=f"{request.topic} — first working arc",
            outcome=f"Make visible progress toward: {request.goal}",
            mastery_items=[
                f"Explain the smallest working version of {request.topic}",
                "Run one bounded experiment",
                "Record one useful result and one failure",
            ],
            lesson_markdown=(
                f"# Task 1 — Build the smallest {request.topic} experiment\n\n"
                "Run one bounded experiment. Record what worked, what failed, "
                "and one question for the next lesson.\n"
            ),
            duration_minutes=35,
        )

    def create_next_lesson(self, run: LearningRun, reflection: str) -> LessonPlan:
        focus = "Compare two chunk sizes" if "chunk" in reflection.lower() else "Investigate the reported gap"
        return LessonPlan(
            title=f"{run.request.topic} — adaptive task {run.current_lesson + 1}",
            outcome=f"Respond to the learner's evidence: {reflection}",
            mastery_items=run.plan.mastery_items,
            lesson_markdown=(
                f"# Task {run.current_lesson + 1} — {focus}\n\n"
                "Repeat the smallest experiment with one controlled change. "
                "Record the before-and-after result.\n"
            ),
            duration_minutes=35,
        )


class InMemoryRunStore:
    def __init__(self) -> None:
        self.runs: dict[str, LearningRun] = {}

    def get_by_idempotency_key(self, key: str) -> LearningRun | None:
        return self.runs.get(key)

    def save(self, run: LearningRun) -> None:
        self.runs[run.idempotency_key] = run

    def get_by_run_id(self, run_id: str) -> LearningRun | None:
        return next((run for run in self.runs.values() if run.run_id == run_id), None)


class InMemoryGateway:
    def __init__(self, free_slot: datetime | None) -> None:
        self.free_slot = free_slot
        self.notion_writes = 0
        self.notion_updates = 0
        self.calendar_writes = 0

    def create_notion_page(self, request: LearningRequest, plan: LessonPlan) -> tuple[str, str]:
        self.notion_writes += 1
        return "notion-page-1", "https://notion.test/notion-page-1"

    def find_free_slot(self, request: LearningRequest, duration_minutes: int) -> datetime | None:
        return self.free_slot

    def create_calendar_event(
        self, request: LearningRequest, plan: LessonPlan, start: datetime
    ) -> tuple[str, str]:
        self.calendar_writes += 1
        event_id = f"calendar-event-{self.calendar_writes}"
        return event_id, f"https://calendar.test/{event_id}"

    def update_notion_page(self, page_id: str, plan: LessonPlan) -> None:
        self.notion_updates += 1
