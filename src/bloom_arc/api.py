from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

from .agent_service import LearningAgentService
from .models import LearningRequest, LearningRun
from .orchestrator import BloomArcOrchestrator
from .ports import AppGateway, BloomPlanner, RunStore
from .settings import Settings
from .testing import InMemoryGateway, InMemoryRunStore, StaticBloomPlanner


class CompletionRequest(BaseModel):
    reflection: str = Field(min_length=3, max_length=2000)


def _receipt(run: LearningRun, *, duplicate_writes: int = 0) -> dict[str, object]:
    return {
        **run.model_dump(mode="json"),
        "actions": {
            "notion": "created" if run.notion_page_id else "failed",
            "calendar": "created" if run.calendar_event_id else "needs_scheduling",
            "duplicate_writes": duplicate_writes,
        },
    }


def _runtime(settings: Settings) -> tuple[BloomPlanner, AppGateway, RunStore]:
    store = InMemoryRunStore()
    if settings.bloom_arc_mode in {"mock", "agent"}:
        gateway = InMemoryGateway(
            free_slot=datetime.now(timezone.utc).replace(microsecond=0)
            + timedelta(days=1)
        )
        return StaticBloomPlanner(), gateway, store

    if settings.bloom_arc_mode != "live":
        raise ValueError("BLOOM_ARC_MODE must be 'mock', 'agent', or 'live'")
    if not settings.notion_parent_page_id:
        raise ValueError("NOTION_PARENT_PAGE_ID is required in live mode")

    from .composio_gateway import ComposioGateway, create_composio_session
    from .planner import create_openai_planner

    session = create_composio_session(settings.bloom_arc_user_id)
    gateway = ComposioGateway(
        session=session,
        notion_parent_page_id=settings.notion_parent_page_id,
        availability_start=settings.availability_start,
        availability_end=settings.availability_end,
    )
    return create_openai_planner(settings.openai_model), gateway, store


def create_app(
    settings: Settings | None = None,
    agent_factory: Callable[[], Any] | None = None,
) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="Learning Arc", version="0.2.0")
    planner, gateway, store = _runtime(settings)
    service = BloomArcOrchestrator(planner, gateway, store)
    agent_service: LearningAgentService | None = None

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": settings.bloom_arc_mode}

    @app.post("/api/runs", status_code=status.HTTP_201_CREATED)
    def start_run(
        request: LearningRequest,
        response: Response,
        idempotency_key: str = Header(alias="Idempotency-Key"),
    ) -> dict[str, object]:
        existing = store.get_by_idempotency_key(idempotency_key)
        run = service.start(request, idempotency_key)
        if existing is not None:
            response.status_code = status.HTTP_200_OK
        return _receipt(run)

    @app.post("/api/agent", status_code=status.HTTP_201_CREATED)
    def run_agent(
        request: LearningRequest,
        idempotency_key: str = Header(alias="Idempotency-Key"),
    ) -> dict[str, object]:
        nonlocal agent_service
        if settings.bloom_arc_mode != "agent":
            raise HTTPException(
                status_code=503,
                detail="Set BLOOM_ARC_MODE=agent to enable the Deep Agent endpoint",
            )
        if agent_service is None:
            if agent_factory is None:
                from .deep_agent import create_learning_arc_agent

                graph = create_learning_arc_agent(settings)
            else:
                graph = agent_factory()
            from .observability import create_lemma_callback

            agent_service = LearningAgentService(
                graph,
                callback_factory=create_lemma_callback,
            )
        return agent_service.run(request, idempotency_key).model_dump(mode="json")

    @app.post("/api/runs/{run_id}/complete")
    def complete_run(run_id: str, body: CompletionRequest) -> dict[str, object]:
        try:
            run = service.complete(run_id, body.reflection)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return _receipt(run)

    return app


app = create_app()
