from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx

from .models import LearningRequest


USAGE = (
    "Usage: `!learn topic | goal | availability | timezone`\n"
    "Example: `!learn RAG | build a small demo | Tuesday evening | Asia/Kolkata`"
)


def parse_learn_command(content: str, user_id: str) -> LearningRequest:
    if not content.lower().startswith("!learn "):
        raise ValueError(USAGE)
    parts = [part.strip() for part in content[7:].split("|")]
    if len(parts) not in (3, 4) or any(not part for part in parts):
        raise ValueError(USAGE)
    topic, goal, availability = parts[:3]
    timezone = parts[3] if len(parts) == 4 else "UTC"
    return LearningRequest(
        user_id=f"discord:{user_id}",
        topic=topic,
        goal=goal,
        availability=availability,
        timezone=timezone,
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

    @client.event
    async def on_ready() -> None:
        print(f"Learning Arc connected as {client.user}")

    @client.event
    async def on_message(message: Any) -> None:
        if message.author == client.user or not message.content.lower().startswith("!learn"):
            return
        try:
            learning_request = parse_learn_command(message.content, str(message.author.id))
        except ValueError as exc:
            await message.reply(str(exc))
            return

        async with message.channel.typing():
            async with httpx.AsyncClient(timeout=90) as http:
                response = await http.post(
                    f"{api_url}/api/agent",
                    headers={"Idempotency-Key": f"discord-message-{message.id}"},
                    json=learning_request.model_dump(),
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
