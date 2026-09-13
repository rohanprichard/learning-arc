from datetime import datetime, timezone

from bloom_arc.models import LearningRequest, RunStatus
from bloom_arc.orchestrator import BloomArcOrchestrator
from bloom_arc.testing import InMemoryGateway, InMemoryRunStore, StaticBloomPlanner


def request() -> LearningRequest:
    return LearningRequest(
        user_id="discord:42",
        topic="RAG",
        goal="build a small demo",
        availability="Tuesday and Thursday evenings",
        timezone="Asia/Kolkata",
    )


def test_start_creates_one_notion_page_and_one_calendar_event() -> None:
    gateway = InMemoryGateway(
        free_slot=datetime(2026, 9, 15, 19, 0, tzinfo=timezone.utc)
    )
    store = InMemoryRunStore()
    service = BloomArcOrchestrator(StaticBloomPlanner(), gateway, store)

    run = service.start(request(), idempotency_key="discord-message-123")

    assert run.status is RunStatus.SCHEDULED
    assert run.notion_page_id == "notion-page-1"
    assert run.calendar_event_id == "calendar-event-1"
    assert gateway.notion_writes == 1
    assert gateway.calendar_writes == 1


def test_repeated_message_returns_existing_run_without_duplicate_writes() -> None:
    gateway = InMemoryGateway(
        free_slot=datetime(2026, 9, 15, 19, 0, tzinfo=timezone.utc)
    )
    store = InMemoryRunStore()
    service = BloomArcOrchestrator(StaticBloomPlanner(), gateway, store)

    first = service.start(request(), idempotency_key="discord-message-123")
    repeated = service.start(request(), idempotency_key="discord-message-123")

    assert repeated.run_id == first.run_id
    assert gateway.notion_writes == 1
    assert gateway.calendar_writes == 1


def test_full_calendar_preserves_notion_plan_without_inventing_a_time() -> None:
    gateway = InMemoryGateway(free_slot=None)
    store = InMemoryRunStore()
    service = BloomArcOrchestrator(StaticBloomPlanner(), gateway, store)

    run = service.start(request(), idempotency_key="discord-message-456")

    assert run.status is RunStatus.NEEDS_SCHEDULING
    assert run.notion_page_id == "notion-page-1"
    assert run.calendar_event_id is None
    assert run.scheduled_start is None
    assert gateway.calendar_writes == 0


def test_completion_generates_only_one_adaptive_next_lesson() -> None:
    gateway = InMemoryGateway(
        free_slot=datetime(2026, 9, 17, 19, 0, tzinfo=timezone.utc)
    )
    store = InMemoryRunStore()
    service = BloomArcOrchestrator(StaticBloomPlanner(), gateway, store)
    run = service.start(request(), idempotency_key="discord-message-789")

    advanced = service.complete(
        run.run_id,
        reflection="The right notes appeared, but every chunk was too broad.",
    )

    assert advanced.current_lesson == 2
    assert "chunk" in advanced.plan.lesson_markdown.lower()
    assert gateway.notion_updates == 1
    assert gateway.calendar_writes == 2
