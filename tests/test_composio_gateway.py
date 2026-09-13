from datetime import datetime

from bloom_arc.composio_gateway import ComposioGateway
from bloom_arc.models import LearningRequest, LessonPlan


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def execute(self, tool: str, arguments: dict) -> dict:
        self.calls.append((tool, arguments))
        if tool == "NOTION_CREATE_NOTION_PAGE":
            return {"successful": True, "data": {"id": "page-1", "url": "https://notion.so/page-1"}}
        if tool == "GOOGLECALENDAR_FIND_FREE_SLOTS":
            return {
                "successful": True,
                "data": {
                    "free_slots": [
                        {"start": "2026-09-15T18:30:00+05:30", "end": "2026-09-15T19:05:00+05:30"}
                    ]
                },
            }
        if tool == "GOOGLECALENDAR_CREATE_EVENT":
            return {"successful": True, "data": {"id": "event-1", "htmlLink": "https://calendar.google.com/event-1"}}
        raise AssertionError(f"Unexpected tool: {tool}")


def request() -> LearningRequest:
    return LearningRequest(
        user_id="discord:42",
        topic="RAG",
        goal="build a demo",
        availability="Tuesday evening",
        timezone="Asia/Kolkata",
    )


def plan() -> LessonPlan:
    return LessonPlan(
        title="RAG — first working arc",
        outcome="Build one retrieval experiment",
        mastery_items=["Run retrieval", "Inspect one failure"],
        lesson_markdown="# Task 1\n\nRun retrieval on five notes.",
        duration_minutes=35,
    )


def test_gateway_uses_narrow_composio_tools_for_notion_and_calendar() -> None:
    session = FakeSession()
    gateway = ComposioGateway(
        session=session,
        notion_parent_page_id="parent-1",
        availability_start="2026-09-15T18:00:00+05:30",
        availability_end="2026-09-15T22:00:00+05:30",
    )

    page_id, _ = gateway.create_notion_page(request(), plan())
    slot = gateway.find_free_slot(request(), 35)
    event_id, _ = gateway.create_calendar_event(request(), plan(), slot)

    assert page_id == "page-1"
    assert slot == datetime.fromisoformat("2026-09-15T18:30:00+05:30")
    assert event_id == "event-1"
    assert [name for name, _ in session.calls] == [
        "NOTION_CREATE_NOTION_PAGE",
        "GOOGLECALENDAR_FIND_FREE_SLOTS",
        "GOOGLECALENDAR_CREATE_EVENT",
    ]
