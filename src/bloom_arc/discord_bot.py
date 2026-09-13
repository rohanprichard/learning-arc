from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx


class ConversationRouter:
    """Route DMs and natural mentions, then keep that conversation active."""

    def __init__(self) -> None:
        self.active: set[tuple[str, str]] = set()

    def should_respond(
        self,
        *,
        is_dm: bool,
        bot_mentioned: bool,
        channel_id: str,
        user_id: str,
    ) -> bool:
        key = (channel_id, user_id)
        if is_dm or bot_mentioned:
            self.active.add(key)
            return True
        return key in self.active


def clean_message(content: str, bot_user_id: str) -> str:
    return (
        content.replace(f"<@{bot_user_id}>", "")
        .replace(f"<@!{bot_user_id}>", "")
        .strip()
    )


def format_run_reply(run: dict[str, Any]) -> str:
    if run.get("final_message"):
        duplicate = "\n`duplicate request — existing agent run reused`" if run.get("duplicate") else ""
        return f"{run['final_message']}\n`run {run.get('run_id', 'unknown')}`{duplicate}"
    plan = run.get("plan") or {}
    lines = [
        f"**Your next arc:** {plan.get('title', 'Learning task')}",
        f"**Timebox:** {plan.get('duration_minutes', 35)} minutes",
    ]
    if run.get("notion_url"):
        lines.append(f"**Notion:** {run['notion_url']}")
    if run.get("calendar_url"):
        lines.append(f"**Calendar:** {run['calendar_url']}")
    else:
        lines.append("**Calendar:** needs scheduling — I did not invent a time.")
    lines.append(f"`run {run.get('run_id', 'unknown')}`")
    return "\n".join(lines)


async def run_bot() -> None:
    try:
        import discord
    except ImportError as exc:
        raise RuntimeError("Install the agent extra: uv sync --extra agent") from exc

    token = os.environ["DISCORD_BOT_TOKEN"]
    api_url = os.getenv("BLOOM_ARC_API_URL", "http://127.0.0.1:8000")
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    router = ConversationRouter()

    @client.event
    async def on_ready() -> None:
        print(f"Learning Arc connected as {client.user}")

    @client.event
    async def on_message(message: Any) -> None:
        if message.author == client.user or client.user is None:
            return

        user_id = str(message.author.id)
        channel_id = str(message.channel.id)
        if not router.should_respond(
            is_dm=message.guild is None,
            bot_mentioned=client.user in message.mentions,
            channel_id=channel_id,
            user_id=user_id,
        ):
            return

        content = clean_message(message.content, str(client.user.id))
        if not content:
            await message.reply("What would you like to learn, and what would progress look like for you?")
            return

        async with message.channel.typing():
            async with httpx.AsyncClient(timeout=180) as http:
                response = await http.post(
                    f"{api_url}/api/agent/chat",
                    headers={"Idempotency-Key": f"discord-message-{message.id}"},
                    json={
                        "user_id": f"discord:{user_id}",
                        "conversation_id": f"discord-channel-{channel_id}-user-{user_id}",
                        "message": content,
                    },
                )
        if response.is_success:
            await message.reply(format_run_reply(response.json()))
        else:
            await message.reply(
                f"I could not finish the run. API returned {response.status_code}; no success was claimed."
            )

    await client.start(token)


if __name__ == "__main__":
    asyncio.run(run_bot())
