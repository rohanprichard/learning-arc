from __future__ import annotations

from uuid import uuid4

from .models import LearningRequest, LearningRun, RunStatus
from .ports import AppGateway, BloomPlanner, RunStore


class BloomArcOrchestrator:
    def __init__(self, planner: BloomPlanner, gateway: AppGateway, store: RunStore) -> None:
        self.planner = planner
        self.gateway = gateway
        self.store = store

    def start(self, request: LearningRequest, idempotency_key: str) -> LearningRun:
        existing = self.store.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return existing

        plan = self.planner.create_first_lesson(request)
        page_id, page_url = self.gateway.create_notion_page(request, plan)
        slot = self.gateway.find_free_slot(request, plan.duration_minutes)

        run = LearningRun(
            run_id=str(uuid4()),
            idempotency_key=idempotency_key,
            request=request,
            plan=plan,
            status=RunStatus.NEEDS_SCHEDULING,
            notion_page_id=page_id,
            notion_url=page_url,
        )
        if slot is not None:
            event_id, event_url = self.gateway.create_calendar_event(request, plan, slot)
            run.status = RunStatus.SCHEDULED
            run.calendar_event_id = event_id
            run.calendar_url = event_url
            run.scheduled_start = slot

        self.store.save(run)
        return run

    def complete(self, run_id: str, reflection: str) -> LearningRun:
        run = self.store.get_by_run_id(run_id)
        if run is None:
            raise KeyError(f"Unknown run: {run_id}")

        next_plan = self.planner.create_next_lesson(run, reflection)
        if run.notion_page_id is not None:
            self.gateway.update_notion_page(run.notion_page_id, next_plan)
        slot = self.gateway.find_free_slot(run.request, next_plan.duration_minutes)

        run.plan = next_plan
        run.current_lesson += 1
        run.last_reflection = reflection
        run.status = RunStatus.NEEDS_SCHEDULING
        run.calendar_event_id = None
        run.calendar_url = None
        run.scheduled_start = None
        if slot is not None:
            event_id, event_url = self.gateway.create_calendar_event(
                run.request, next_plan, slot
            )
            run.status = RunStatus.SCHEDULED
            run.calendar_event_id = event_id
            run.calendar_url = event_url
            run.scheduled_start = slot
        self.store.save(run)
        return run
