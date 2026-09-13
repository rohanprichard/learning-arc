import pytest

from bloom_arc.discord_bot import format_run_reply, parse_learn_command


def test_parse_learn_command_extracts_bounded_fields() -> None:
    parsed = parse_learn_command(
        "!learn RAG | build a small demo | Tuesday and Thursday evenings | Asia/Kolkata",
        user_id="42",
    )

    assert parsed.topic == "RAG"
    assert parsed.goal == "build a small demo"
    assert parsed.availability == "Tuesday and Thursday evenings"
    assert parsed.timezone == "Asia/Kolkata"


def test_parse_learn_command_rejects_missing_fields() -> None:
    with pytest.raises(ValueError, match="Usage"):
        parse_learn_command("!learn RAG", user_id="42")


def test_format_reply_surfaces_partial_state_honestly() -> None:
    reply = format_run_reply(
        {
            "run_id": "run-1",
            "status": "needs_scheduling",
            "notion_url": "https://notion.so/page-1",
            "calendar_url": None,
            "plan": {"title": "RAG arc", "duration_minutes": 35},
        }
    )

    assert "Notion" in reply
    assert "needs scheduling" in reply.lower()
    assert "scheduled" not in reply.lower()
