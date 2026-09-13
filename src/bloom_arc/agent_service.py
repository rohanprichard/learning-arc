from __future__ import annotations

from copy import deepcopy
from collections.abc import Callable
from typing import Any, Protocol
from uuid import uuid4

from .models import AgentRun, LearningRequest


class InvokableAgent(Protocol):
    def invoke(self, input: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]: ...


class LearningAgentService:
    """Reliability boundary around the reasoning-and-action agent loop."""

    def __init__(
        self,
        agent: InvokableAgent,
        callback_factory: Callable[[], Any | None] | None = None,
    ) -> None:
        self.agent = agent
        self.callback_factory = callback_factory
        self._runs: dict[str, AgentRun] = {}

    def run(self, request: LearningRequest, idempotency_key: str) -> AgentRun:
        return self._invoke(
            message=self._prompt(request),
            user_id=request.user_id,
            thread_id=idempotency_key,
            idempotency_key=idempotency_key,
        )

    def chat(
        self,
        *,
        message: str,
        user_id: str,
        thread_id: str,
        idempotency_key: str,
    ) -> AgentRun:
        return self._invoke(
            message=f"Learner message:\n{message}",
            user_id=user_id,
            thread_id=thread_id,
            idempotency_key=idempotency_key,
        )

    def _invoke(
        self,
        *,
        message: str,
        user_id: str,
        thread_id: str,
        idempotency_key: str,
    ) -> AgentRun:
        existing = self._runs.get(idempotency_key)
        if existing is not None:
            repeated = existing.model_copy(deep=True)
            repeated.duplicate = True
            return repeated

        config: dict[str, Any] = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        if self.callback_factory is not None:
            callback = self.callback_factory()
            if callback is not None:
                config["callbacks"] = [callback]
                config["configurable"]["user_id"] = user_id

        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
        )
        messages = result.get("messages", [])
        final_message = self._content(messages[-1]) if messages else "Agent returned no message."
        run = AgentRun(
            run_id=str(uuid4()),
            idempotency_key=idempotency_key,
            status="completed",
            final_message=final_message,
            tool_calls=self._tool_calls(messages),
        )
        self._runs[idempotency_key] = deepcopy(run)
        return run

    @staticmethod
    def _prompt(request: LearningRequest) -> str:
        return f"""Act as the Learning Arc agent. Load and follow the Bloom Tutor skill.
You must decide the smallest useful first lesson, then take action across the
allowed external apps. Create or update the learning page in Notion, inspect
Google Calendar availability, and create a study event only if a real free slot
exists. Return an honest action receipt with object links/IDs. Do not claim an
action succeeded unless its tool result confirms success.

Learner: {request.user_id}
Topic: {request.topic}
Goal: {request.goal}
Availability: {request.availability}
Timezone: {request.timezone}
"""

    @staticmethod
    def _content(message: Any) -> str:
        if isinstance(message, dict):
            return str(message.get("content", ""))
        return str(getattr(message, "content", ""))

    @staticmethod
    def _tool_calls(messages: list[Any]) -> list[str]:
        names: list[str] = []
        for message in messages:
            calls = message.get("tool_calls", []) if isinstance(message, dict) else getattr(message, "tool_calls", [])
            for call in calls or []:
                if isinstance(call, dict) and call.get("name"):
                    names.append(str(call["name"]))
        return names
