from bloom_arc.agent_service import LearningAgentService
from bloom_arc.models import LearningRequest


class FakeDeepAgent:
    def __init__(self) -> None:
        self.invocations = 0
        self.last_input = None
        self.last_config = None

    def invoke(self, input, config):
        self.invocations += 1
        self.last_input = input
        self.last_config = config
        return {
            "messages": [
                {"role": "assistant", "content": "I created one lesson and scheduled it."}
            ]
        }


def request() -> LearningRequest:
    return LearningRequest(
        user_id="discord:42",
        topic="RAG",
        goal="build a demo",
        availability="Tuesday evening",
        timezone="Asia/Kolkata",
    )


def test_learning_agent_invokes_a_tool_using_agent_with_stable_thread() -> None:
    graph = FakeDeepAgent()
    service = LearningAgentService(graph)

    result = service.run(request(), idempotency_key="discord-message-1")

    assert result.status == "completed"
    assert graph.invocations == 1
    assert graph.last_config == {"configurable": {"thread_id": "discord-message-1"}}
    prompt = graph.last_input["messages"][0]["content"]
    assert "RAG" in prompt
    assert "decide" in prompt.lower()
    assert "Notion" in prompt
    assert "Google Calendar" in prompt


def test_learning_agent_caches_repeated_message_before_agent_reacts() -> None:
    graph = FakeDeepAgent()
    service = LearningAgentService(graph)

    first = service.run(request(), idempotency_key="discord-message-1")
    repeated = service.run(request(), idempotency_key="discord-message-1")

    assert repeated.run_id == first.run_id
    assert repeated.duplicate is True
    assert graph.invocations == 1
