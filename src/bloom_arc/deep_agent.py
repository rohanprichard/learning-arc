from __future__ import annotations

import os
from pathlib import Path

from .settings import Settings


SYSTEM_PROMPT = """You are Learning Arc, a multi-app adaptive learning agent.
You perceive the learner's intent, decide the next pedagogical action, use tools,
observe each result, recover from failures, and continue until the learner has an
honest next step. Load the Learning Arc Tutor skill before planning. Use only the
Composio tools available to you. Never claim success without observing it.
If Google Tasks tools are available, create one current task after the Notion page
exists and include the Notion link; this is optional and must not block the core.
"""


def create_learning_arc_agent(settings: Settings):
    """Build the real Deep Agent with Bloom skills and restricted Composio tools."""
    from composio import Composio
    from composio_langchain import LangchainProvider
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    from deepagents.middleware import FilesystemMiddleware
    from langchain_openai import ChatOpenAI

    if not os.environ.get("COMPOSIO_API_KEY"):
        raise ValueError("COMPOSIO_API_KEY is required for agent mode")

    project_root = Path(__file__).resolve().parents[2]
    backend = FilesystemBackend(root_dir=project_root, virtual_mode=True)
    filesystem = FilesystemMiddleware(
        backend=backend,
        tools=["read_file", "ls", "glob", "grep"],
    )

    toolkits = ["notion", "googlecalendar"]
    allowed_tools = {
        "notion": {
            "enable": [
                "NOTION_SEARCH_NOTION_PAGE",
                "NOTION_CREATE_NOTION_PAGE",
                "NOTION_GET_PAGE_MARKDOWN",
                "NOTION_ADD_MULTIPLE_PAGE_CONTENT",
            ]
        },
        "googlecalendar": {
            "enable": [
                "GOOGLECALENDAR_FIND_EVENT",
                "GOOGLECALENDAR_FIND_FREE_SLOTS",
                "GOOGLECALENDAR_CREATE_EVENT",
            ]
        },
    }
    if settings.enable_google_tasks:
        toolkits.append("googletasks")
        allowed_tools["googletasks"] = {
            "enable": [
                "GOOGLETASKS_LIST_TASK_LISTS",
                "GOOGLETASKS_INSERT_TASK",
                "GOOGLETASKS_GET_TASK",
                "GOOGLETASKS_PATCH_TASK",
            ]
        }

    composio = Composio(provider=LangchainProvider())
    session = composio.create(
        user_id=settings.bloom_arc_user_id,
        toolkits=toolkits,
        tools=allowed_tools,
        sandbox={"enable": False},
    )

    model_name = settings.agent_model
    if model_name.startswith("openrouter:"):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required for an OpenRouter model")
        model = ChatOpenAI(
            model=model_name.removeprefix("openrouter:"),
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            temperature=0,
        )
    else:
        model = model_name

    return create_deep_agent(
        model=model,
        tools=session.tools(),
        system_prompt=SYSTEM_PROMPT,
        skills=["./skills/"],
        backend=backend,
        middleware=[filesystem],
        checkpointer=True,
        name="learning_arc",
    )
