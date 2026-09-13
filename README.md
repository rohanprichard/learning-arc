# Learning Arc

**An adaptive learning arc that bends around your real week.**

Learning Arc connects the open-source Bloom Tutor learning method to Discord, Notion, and Google Calendar. A learner asks to learn a topic in Discord; Learning Arc generates one measurable task, publishes it to Notion, checks for a real free slot, schedules it, and adapts the next task from the learner's reflection.

## Why this stack

- **Python + FastAPI** for the API and visible action receipts.
- **discord.py** for a reliable incoming Discord interface.
- **LangChain Deep Agents** for the actual reasoning → tool call → observation → recovery loop and progressive loading of the Bloom-derived skill.
- **Composio Sessions** for narrowly allow-listed Notion and Google Calendar tools and OAuth.
- **Google Tasks (optional fourth app)** for the one current action, linked back to the Notion lesson.
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

## One path to run everything

```bash
cp .env.example .env
```

Put only these values in `.env`:

```dotenv
COMPOSIO_API_KEY=your-key
OPENROUTER_API_KEY=your-key
DISCORD_BOT_TOKEN=your-token
ENABLE_GOOGLE_TASKS=true
```

Then run one command:

```bash
./run.sh
```

`run.sh` validates the three required credentials, builds the Docker image, and starts the FastAPI API plus Discord bot together through Docker Compose. FastAPI is exposed only on `127.0.0.1:8000`. The agent model and stable demo user ID have defaults in code, so they do not belong in `.env`.

Connect the same Composio user to the **Notion** and **Google Calendar** toolkits. Connect **Google Tasks** too if the optional fourth app is enabled. OAuth must be completed by the account owner; the app does not request or store those credentials. The Deep Agent discovers schemas, calls the allowed tools, observes the results, and continues until it can return an honest action receipt.

In the test channel:

```text
!learn RAG | build a small demo | Tuesday and Thursday evenings | Asia/Kolkata
```

The bot uses the Discord message ID as the idempotency key.

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

## Reliability scenarios

1. **Happy path:** one Notion page and one Calendar event.
2. **Duplicate message:** the existing run is returned; no duplicate writes.
3. **No free slot:** Notion succeeds, Calendar remains empty, status is `needs_scheduling`.
4. **Adaptive completion:** one learner reflection creates exactly one next lesson and one next session.

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
