from __future__ import annotations

import os
from typing import Any


def create_lemma_callback() -> Any | None:
    """Create one Lemma LangGraph callback per Learning Arc execution."""
    api_key = os.getenv("LEMMA_API_KEY")
    project_id = os.getenv("LEMMA_PROJECT_ID")
    if not api_key and not project_id:
        return None
    if not api_key:
        raise ValueError("LEMMA_API_KEY is required when LEMMA_PROJECT_ID is set")
    if not project_id:
        raise ValueError("LEMMA_PROJECT_ID is required when LEMMA_API_KEY is set")

    from uselemma_tracing import langgraph

    return langgraph(
        api_key=api_key,
        project_id=project_id,
        agent_name="learning-arc",
        release=os.getenv("LEMMA_RELEASE", "hackathon-2026"),
    )
