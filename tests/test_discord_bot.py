from bloom_arc.discord_bot import ConversationRouter, clean_message, format_run_reply


def test_direct_messages_need_no_trigger_phrase() -> None:
    router = ConversationRouter()

    assert router.should_respond(
        is_dm=True,
        bot_mentioned=False,
        channel_id="dm-1",
        user_id="42",
    )


def test_first_server_message_uses_a_natural_mention_then_followups_are_freeform() -> None:
    router = ConversationRouter()

    assert router.should_respond(
        is_dm=False,
        bot_mentioned=True,
        channel_id="channel-9",
        user_id="42",
    )
    assert router.should_respond(
        is_dm=False,
        bot_mentioned=False,
        channel_id="channel-9",
        user_id="42",
    )
    assert not router.should_respond(
        is_dm=False,
        bot_mentioned=False,
        channel_id="channel-9",
        user_id="different-user",
    )


def test_clean_message_removes_discord_mention_without_structured_parsing() -> None:
    assert clean_message(
        "<@123> I want to learn RAG, but I only have Tuesday evening.",
        bot_user_id="123",
    ) == "I want to learn RAG, but I only have Tuesday evening."


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
