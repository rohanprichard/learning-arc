import asyncio

import pytest

from bloom_arc.__main__ import run_all


@pytest.mark.asyncio
async def test_run_all_starts_api_and_bot_and_cancels_peer_on_exit() -> None:
    started: list[str] = []
    bot_cancelled = asyncio.Event()

    async def api() -> None:
        started.append("api")
        await asyncio.sleep(0)

    async def bot() -> None:
        started.append("bot")
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            bot_cancelled.set()
            raise

    await run_all(api, bot)

    assert set(started) == {"api", "bot"}
    assert bot_cancelled.is_set()
