from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool


class ToolCapableFakeModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        return self


def test_deep_agent_loads_skill_observes_tools_and_completes_arc() -> None:
    calls: list[tuple[str, str]] = []

    @tool
    def create_notion_page(title: str) -> str:
        """Create a test Notion page."""
        calls.append(("notion", title))
        return "notion-page-1"

    @tool
    def find_free_slot(timezone: str) -> str:
        """Find a test free slot."""
        calls.append(("free", timezone))
        return "2026-09-15T18:30:00+05:30"

    @tool
    def create_calendar_event(start: str) -> str:
        """Create a test calendar event."""
        calls.append(("calendar", start))
        return "calendar-event-1"

    model = ToolCapableFakeModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "read_file",
                        "args": {"file_path": "./skills/learning-arc-tutor/SKILL.md"},
                        "id": "skill-1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "create_notion_page",
                        "args": {"title": "RAG — first arc"},
                        "id": "notion-1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "find_free_slot",
                        "args": {"timezone": "Asia/Kolkata"},
                        "id": "free-1",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "create_calendar_event",
                        "args": {"start": "2026-09-15T18:30:00+05:30"},
                        "id": "calendar-1",
                    }
                ],
            ),
            AIMessage(
                content="Created one adaptive lesson in Notion and scheduled a confirmed free slot."
            ),
        ]
    )
    agent = create_deep_agent(
        model=model,
        tools=[create_notion_page, find_free_slot, create_calendar_event],
        skills=["./skills/"],
        backend=FilesystemBackend(root_dir=Path.cwd(), virtual_mode=True),
        name="learning_arc_offline_e2e",
    )

    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Help me learn RAG"}]}
    )

    assert calls == [
        ("notion", "RAG — first arc"),
        ("free", "Asia/Kolkata"),
        ("calendar", "2026-09-15T18:30:00+05:30"),
    ]
    assert "confirmed free slot" in result["messages"][-1].content
