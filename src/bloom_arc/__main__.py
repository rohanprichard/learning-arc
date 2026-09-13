from __future__ import annotations

import asyncio
import os
from collections.abc import Callable, Coroutine
from typing import Any

import uvicorn

from .discord_bot import run_bot


async def serve_api() -> None:
    config = uvicorn.Config(
        "bloom_arc.api:app",
        host=os.getenv("LEARNING_ARC_HOST", "127.0.0.1"),
        port=int(os.getenv("LEARNING_ARC_PORT", "8000")),
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_all(
    api_factory: Callable[[], Coroutine[Any, Any, None]],
    bot_factory: Callable[[], Coroutine[Any, Any, None]],
) -> None:
    tasks = {
        asyncio.create_task(api_factory(), name="learning-arc-api"),
        asyncio.create_task(bot_factory(), name="learning-arc-discord"),
    }
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    for task in done:
        task.result()


async def main() -> None:
    await run_all(serve_api, run_bot)


if __name__ == "__main__":
    asyncio.run(main())
