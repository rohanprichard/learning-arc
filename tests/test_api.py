from fastapi.testclient import TestClient

from bloom_arc.api import create_app
from bloom_arc.settings import Settings


class FakeDeepAgent:
    def invoke(self, input, config):
        return {"messages": [{"role": "assistant", "content": "Agent created the learning arc."}]}


def test_health_reports_mock_mode() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "mock"}


def test_start_endpoint_returns_visible_action_receipt() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/runs",
        headers={"Idempotency-Key": "discord-message-123"},
        json={
            "user_id": "discord:42",
            "topic": "RAG",
            "goal": "build a small demo",
            "availability": "Tuesday and Thursday evenings",
            "timezone": "Asia/Kolkata",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "scheduled"
    assert body["actions"]["notion"] == "created"
    assert body["actions"]["calendar"] == "created"
    assert body["actions"]["duplicate_writes"] == 0


def test_agent_endpoint_runs_the_real_agent_boundary() -> None:
    client = TestClient(
        create_app(
            settings=Settings(bloom_arc_mode="agent"),
            agent_factory=lambda: FakeDeepAgent(),
        )
    )

    response = client.post(
        "/api/agent",
        headers={"Idempotency-Key": "discord-message-agent-1"},
        json={
            "user_id": "discord:42",
            "topic": "RAG",
            "goal": "build a small demo",
            "availability": "Tuesday evening",
            "timezone": "Asia/Kolkata",
        },
    )

    assert response.status_code == 201
    assert response.json()["final_message"] == "Agent created the learning arc."
