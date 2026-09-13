# Learning Arc

**Learning Arc turns a learner’s ordinary Discord message into one practical next step that fits their real life.** It asks only for missing context, creates a living learning page, checks the learner’s schedule before booking time, and adapts the next lesson from what the learner reports back.

## Project overview

A learner can start naturally:

> I want to learn RAG for a small project. I know Python, and Tuesday evening usually works for me.

Learning Arc is a Python/FastAPI application powered by a LangChain Deep Agent and a Bloom-inspired adaptive tutoring skill. The agent reasons over the current conversation, decides whether one clarification is necessary, uses external tools, observes their results, and returns an honest response. It does not use command syntax or fixed form fields.

The learning loop is:

```text
natural conversation → one bounded lesson → real study time → learner reflection → adaptive next lesson
```

## External apps used

| App | Learning Arc action |
|---|---|
| **Discord** | Receives free-form learner conversation and returns questions, progress, and action receipts. |
| **Notion** | Searches for or creates the learner’s course page and appends the current lesson. |
| **Google Calendar** | Checks a real free slot before creating a study event. |
| **Google Tasks** *(optional)* | Creates one current task linked to the Notion lesson. |

The required three-app demo is **Discord → Notion → Google Calendar**. Google Tasks is enabled by default as an optional fourth app.

## Setup instructions

### 1. Discord

1. Create a **Learning Arc** app in the [Discord Developer Portal](https://discord.com/developers/applications).
2. On **Bot**, copy the bot token and enable **Message Content Intent**.
3. On **Installation**, add the `bot` scope for Guild Install and install it in a test server.
4. Give it only: **View Channels**, **Send Messages**, **Send Messages in Threads**, **Read Message History**, and **Embed Links**. Do not grant Administrator.

### 2. Composio

1. Create/select a project in the [Composio dashboard](https://dashboard.composio.dev) and copy its API key from **Settings → API Keys**.
2. Connect **Notion** and **Google Calendar** with Composio-managed OAuth.
3. During the Notion authorization flow, share a blank `Learning Arc Demo` page with the integration.
4. Optionally connect **Google Tasks** using the same Google account.

Composio provides the OAuth application for these integrations; no separate Notion or Google Cloud OAuth client is required.

### 3. OpenRouter and run

Create an API key at [OpenRouter](https://openrouter.ai/settings/keys), then:

```bash
cp .env.example .env
```

Fill only these values in `.env`:

```dotenv
COMPOSIO_API_KEY=your-key
OPENROUTER_API_KEY=your-key
DISCORD_BOT_TOKEN=your-token
ENABLE_GOOGLE_TASKS=true
```

Start the complete Docker deployment:

```bash
./run.sh
```

This command builds the image and starts FastAPI plus the Discord bot. The API binds only to `127.0.0.1:8000`.

## Demo flow

1. In a Discord DM, send an ordinary learning request. In a server, mention `@Learning Arc` once to begin.
2. If key information is missing, answer its single natural clarification. Follow-up messages need no command or mention.
3. Verify the learner’s Notion page and Calendar study session directly in the linked apps.
4. Reply with a real observation, e.g. “The retrieved chunks were too broad.”
5. Show Learning Arc create exactly one adapted next lesson and schedule the next available session.

## Reliability testing

Automated test coverage verifies:

- a Deep Agent loads the tutoring skill, calls Notion, checks Calendar availability, observes results, then creates a Calendar event;
- duplicate message delivery does not invoke a second agent run;
- no free Calendar slot results in no Calendar write or invented time;
- learner feedback produces exactly one adaptive next lesson;
- Discord DMs work without a prefix, one server mention starts a conversation, and follow-up messages remain free-form;
- Docker Compose configuration and container startup succeed.

Run the suite:

```bash
uv run pytest
```

**Current persistence boundary:** conversation state and idempotency are retained while the container runs. Notion, Calendar, and Tasks are durable external state. Restarting or recreating the container clears in-memory conversation state; do not restart it during the demo.

## Two-minute demo

**Demo video:** TODO — add publicly accessible video URL before submission.

Suggested recording: show a natural Discord request, one clarification, the Notion page, a conflict-checked Calendar booking, evidence-driven adaptation after learner feedback, and the no-free-slot safety behavior.

## Optional Lemma support

Lemma tracing is already installed and wired for the LangGraph/Deep Agent runtime, but disabled by default so its paid credentials do not block the hackathon build. Add `LEMMA_API_KEY` and `LEMMA_PROJECT_ID` to `.env` later to enable it without a code change.

## Attribution

The tutoring approach is adapted from [Li-Evan/Bloom](https://github.com/Li-Evan/Bloom), an MIT-licensed adaptive tutoring project. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
