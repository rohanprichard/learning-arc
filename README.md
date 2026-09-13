# Learning Arc

**An adaptive learning arc that bends around your real week.**

## Project overview

Learning Arc connects the open-source Bloom Tutor learning method to Discord, Notion, and Google Calendar. A learner asks to learn a topic in Discord; Learning Arc generates one measurable task, publishes it to Notion, checks for a real free slot, schedules it, and adapts the next task from the learner's reflection.

## External apps used

| App | Agent action |
|---|---|
| Discord | Receives free-form learner conversation and returns questions, action receipts, and progress |
| Notion | Searches for or creates the learning page and appends the current adaptive lesson |
| Google Calendar | Finds a real free slot before creating a study event |
| Google Tasks | Optional fourth app: creates one current action linked to the Notion lesson |

Lemma tracing is included as optional observability infrastructure and is not counted among the required external apps.

## Why this stack

- **Python + FastAPI** for the API and visible action receipts.
- **discord.py** for a reliable incoming Discord interface.
- **LangChain Deep Agents** for the actual reasoning → tool call → observation → recovery loop and progressive loading of the Bloom-derived skill.
- **Composio Sessions** for narrowly allow-listed Notion and Google Calendar tools and OAuth.
- **Google Tasks (optional fourth app)** for the one current action, linked back to the Notion lesson.
- **Lemma** traces every LangGraph/Deep Agent execution, model generation, graph node, and Composio tool call for reliability evidence.
- **Deterministic Python guardrails** outside the agent for idempotency and an exact external-tool allowlist.

## Working now

- `POST /api/agent` invokes a real Deep Agent boundary in agent mode.
- The agent loads `skills/learning-arc-tutor/SKILL.md` and decides which allowed Composio tools to call based on observations.
- `POST /api/runs` creates the first lesson flow.
- `POST /api/runs/{run_id}/complete` uses a reflection to create Task 2.
- Repeated Discord message IDs are idempotent within the running process.
- A full calendar returns `needs_scheduling`; no time is invented.
- Mock Notion and Calendar adapters allow a complete local demo without credentials.
- A restricted Deep Agent + Composio factory is included with seven read/create/search tools and no destructive tools.
- A Discord `!learn` interface is included.
- Tests cover orchestration, duplicate prevention, no-slot behavior, adaptation, API receipts, Composio calls, and Discord parsing.

## Allowed external tools

```text
NOTION_SEARCH_NOTION_PAGE
NOTION_CREATE_NOTION_PAGE
NOTION_GET_PAGE_MARKDOWN
NOTION_ADD_MULTIPLE_PAGE_CONTENT
GOOGLECALENDAR_FIND_EVENT
GOOGLECALENDAR_FIND_FREE_SLOTS
GOOGLECALENDAR_CREATE_EVENT

# Optional when ENABLE_GOOGLE_TASKS=true
GOOGLETASKS_LIST_TASK_LISTS
GOOGLETASKS_INSERT_TASK
GOOGLETASKS_GET_TASK
GOOGLETASKS_PATCH_TASK
```

No delete, archive, attendee-invite, or destructive tools are exposed.

## Setup instructions — one path to run everything

### Discord

Create a **Learning Arc** app in the [Discord Developer Portal](https://discord.com/developers/applications). On **Bot**, copy the token and enable **Message Content Intent**. On **Installation**, enable **Guild Install**, select the `bot` scope, and grant only **View Channels**, **Send Messages**, **Send Messages in Threads**, **Read Message History**, and **Embed Links**. Install it in a test server and give it access to the demo channel. Do not grant Administrator.

### Composio

In the [Composio dashboard](https://dashboard.composio.dev), create/select a project and copy its API key from **Settings → API Keys**. Connect **Notion** and **Google Calendar** with Composio-managed OAuth; add **Google Tasks** only when using the optional fourth app. During Notion authorization, grant the integration access to a blank `Learning Arc Demo` page. Composio provides the OAuth application, so no separate Notion or Google Cloud OAuth client is needed.

### OpenRouter and local configuration

Create an OpenRouter key at [OpenRouter API Keys](https://openrouter.ai/settings/keys), then:

```bash
cp .env.example .env
```

Fill only:

```dotenv
COMPOSIO_API_KEY=your-key
OPENROUTER_API_KEY=your-key
DISCORD_BOT_TOKEN=your-token
ENABLE_GOOGLE_TASKS=true
```

Do not commit or share `.env`; it is excluded from Git and the Docker build context.

### Start

```bash
./run.sh
```

The launcher builds the Docker image and starts FastAPI plus the Discord bot.

### Verify

In a DM, simply write:

```text
I want to learn RAG for a small project. I know Python, and Tuesday evening usually works for me.
```

In a server, mention Learning Arc once to begin; follow-up messages in that conversation are free-form. Confirm the Notion page, conflict-checked Calendar event, optional Google Task, and Discord action receipt directly in their apps.

The bot uses each Discord message ID as an idempotency key while the channel/user pair supplies stable multi-turn agent context.

## Optional Lemma observability — included and ready

Learning Arc uses Lemma's official Python LangGraph callback. One Discord request becomes one Lemma trace. Deep Agent graph nodes become spans, LLM calls become generations, and Composio actions become tool-call records with their outputs or errors. The Discord message ID is passed as the trace thread ID and the Discord user ID as the trace user ID.

This makes the reliability claim inspectable in the demo: open the corresponding Lemma trace and show the Notion lookup/write, Calendar availability check, Calendar write or safe no-slot branch, latency, and any tool error. Lemma is observability infrastructure; the three required user-facing apps remain Discord, Notion, and Google Calendar.

Lemma is disabled automatically when its credentials are absent, so it does not block the free hackathon build. To enable it later, add `LEMMA_API_KEY` and `LEMMA_PROJECT_ID` to `.env`; no code change is required.

## Test

```bash
uv run pytest
```

## Architecture

```text
Discord message
    │
    ▼
Discord adapter ──► FastAPI
                      │
                      ▼
               Deep Agent runtime
                │            │
                ▼            ▼
      Bloom-derived skill   Composio router tools
                              │           │
                              ▼           ▼
                           Notion     Google Calendar
```

The agent decides the lesson and the next tool call from observed state. Python still enforces the action boundary, exact tool allowlist, stable thread ID, and duplicate-request cache. This keeps it genuinely agentic without granting arbitrary external access.

## Reliability testing

1. **Happy path:** one Notion page and one Calendar event.
2. **Duplicate message:** the existing run is returned; no duplicate writes.
3. **No free slot:** Notion succeeds, Calendar remains empty, status is `needs_scheduling`.
4. **Adaptive completion:** one learner reflection creates exactly one next lesson and one next session.

Automated coverage exercises the happy path, duplicate delivery, no-slot behavior, adaptive Task 2 generation, natural Discord routing, the Deep Agent tool trajectory, and Docker configuration. Run `docker compose run --rm learning-arc uv run pytest` to reproduce the suite.

**Current persistence boundary:** the Discord thread ID keeps agent conversation context for the lifetime of the running container. Notion, Calendar, and Tasks are durable external state; the in-process idempotency cache and LangGraph checkpointer reset if the container is recreated. For the hackathon demo, do not restart the container mid-conversation.

**Next production hardening:** add a SQLite/Postgres LangGraph checkpointer and durable run/idempotency store so conversational context survives restarts.


## Two-minute demo

**Demo video:** TODO — add the publicly accessible two-minute video URL before submission.

The demo should show: a natural Discord request, one clarifying question if needed, the Notion lesson, the conflict-checked Calendar event, the optional Google Task, and a duplicate/no-slot reliability case.

## Why Google Tasks is the easiest fourth app

It gives the current lesson a distinct execution surface rather than duplicating the Notion document. Learning Arc can create one task containing the Notion link, then later observe its completion before generating the next lesson. It uses a small Composio toolkit and the same Google identity the learner already uses for Calendar. Keep it optional so failure cannot block the required Discord → Notion → Calendar loop.

## Immediate limitations

- Live Composio writes require the user's connected accounts and have not been executed in this repository yet.
- Idempotency currently persists only for the lifetime of the API process; SQLite persistence is the next reliability improvement.
- Natural-language availability is displayed to the learner, while the live demo window is currently supplied by `AVAILABILITY_START` and `AVAILABILITY_END`.
- YouTube references are intentionally deferred until the three-app loop is live.
- The full offline Deep Agent trajectory is tested with an actual Deep Agents runtime and scripted external-tool results. Live Composio OAuth calls remain blocked until accounts are connected.

## Attribution

The tutoring method is adapted from [Li-Evan/Bloom](https://github.com/Li-Evan/Bloom), an MIT-licensed adaptive tutoring project. Learning Arc is the cross-app orchestration layer.
