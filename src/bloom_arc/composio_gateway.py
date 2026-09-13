from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from .models import LearningRequest, LessonPlan


class ComposioSession(Protocol):
    def execute(self, tool: str, arguments: dict[str, Any]) -> Any: ...


def _payload(result: Any) -> dict[str, Any]:
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected Composio response: {type(result).__name__}")
    if result.get("successful") is False:
        raise RuntimeError(str(result.get("error") or result))
    data = result.get("data", result)
    if not isinstance(data, dict):
        raise RuntimeError("Composio response did not contain an object payload")
    return data


class ComposioGateway:
    """Narrow, deterministic Composio adapter for Learning Arc's allowed writes."""

    def __init__(
        self,
        session: ComposioSession,
        notion_parent_page_id: str,
        availability_start: str,
        availability_end: str,
    ) -> None:
        self.session = session
        self.notion_parent_page_id = notion_parent_page_id
        self.availability_start = availability_start
        self.availability_end = availability_end

    def create_notion_page(self, request: LearningRequest, plan: LessonPlan) -> tuple[str, str]:
        markdown = self._page_markdown(request, plan)
        data = _payload(
            self.session.execute(
                "NOTION_CREATE_NOTION_PAGE",
                arguments={
                    "parent_id": self.notion_parent_page_id,
                    "title": plan.title,
                    "markdown": markdown,
                },
            )
        )
        page_id = str(data.get("id") or data.get("page_id") or "")
        if not page_id:
            raise RuntimeError("Notion page creation returned no page id")
        return page_id, str(data.get("url") or data.get("public_url") or "")

    def update_notion_page(self, page_id: str, plan: LessonPlan) -> None:
        _payload(
            self.session.execute(
                "NOTION_ADD_MULTIPLE_PAGE_CONTENT",
                arguments={
                    "page_id": page_id,
                    "content": plan.lesson_markdown,
                },
            )
        )

    def find_free_slot(self, request: LearningRequest, duration_minutes: int) -> datetime | None:
        data = _payload(
            self.session.execute(
                "GOOGLECALENDAR_FIND_FREE_SLOTS",
                arguments={
                    "items": ["primary"],
                    "time_min": self.availability_start,
                    "time_max": self.availability_end,
                    "timezone": request.timezone,
                    "duration_minutes": duration_minutes,
                },
            )
        )
        slots = data.get("free_slots") or data.get("slots") or []
        if not slots:
            return None
        first = slots[0]
        start = first.get("start") if isinstance(first, dict) else first
        return datetime.fromisoformat(str(start).replace("Z", "+00:00"))

    def create_calendar_event(
        self, request: LearningRequest, plan: LessonPlan, start: datetime
    ) -> tuple[str, str]:
        data = _payload(
            self.session.execute(
                "GOOGLECALENDAR_CREATE_EVENT",
                arguments={
                    "calendar_id": "primary",
                    "summary": f"Learning Arc · {plan.title}",
                    "description": f"{plan.outcome}\n\nCreated by Learning Arc for {request.goal}",
                    "start_datetime": start.isoformat(),
                    "event_duration_minutes": plan.duration_minutes,
                    "timezone": request.timezone,
                },
            )
        )
        event_id = str(data.get("id") or data.get("event_id") or "")
        if not event_id:
            raise RuntimeError("Calendar event creation returned no event id")
        return event_id, str(data.get("htmlLink") or data.get("html_link") or data.get("url") or "")

    @staticmethod
    def _page_markdown(request: LearningRequest, plan: LessonPlan) -> str:
        mastery = "\n".join(f"- [ ] {item}" for item in plan.mastery_items)
        return (
            f"> Goal: {request.goal}\n"
            f"> Availability: {request.availability}\n\n"
            f"## Learning outcome\n\n{plan.outcome}\n\n"
            f"## Mastery arc\n\n{mastery}\n\n"
            f"{plan.lesson_markdown}"
        )


def create_composio_session(user_id: str) -> ComposioSession:
    """Create an allow-listed session; imports Composio only in live mode."""
    from composio import Composio

    composio = Composio()
    return composio.create(
        user_id=user_id,
        toolkits=["notion", "googlecalendar"],
        tools={
            "notion": {
                "enable": [
                    "NOTION_CREATE_NOTION_PAGE",
                    "NOTION_ADD_MULTIPLE_PAGE_CONTENT",
                ]
            },
            "googlecalendar": {
                "enable": [
                    "GOOGLECALENDAR_FIND_FREE_SLOTS",
                    "GOOGLECALENDAR_CREATE_EVENT",
                ]
            },
        },
    )
