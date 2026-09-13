# Learning Arc — test report

## Result

**Offline executable system: PASS**  
**Live external-account system: BLOCKED BY AUTHENTICATION**

## What was executed

1. Installed the complete Python environment with the `agent` and `dev` extras.
2. Imported and instantiated LangChain Deep Agents 0.7.13.
3. Created an actual Deep Agent runtime with the project filesystem backend and the Learning Arc skill directory.
4. Executed an offline end-to-end agent trajectory:
   - agent called `read_file` to load the tutor skill;
   - agent called a Notion-page tool;
   - agent observed the returned page ID;
   - agent called a Calendar free-slot tool;
   - agent observed a real fixture slot;
   - agent called a Calendar event tool;
   - agent returned a final evidence-based message.
5. Exercised FastAPI endpoints with `TestClient`.
6. Tested natural-language Discord routing: DMs need no prefix, one server mention starts a conversation, and follow-up replies remain free-form.
7. Tested Discord response formatting.
8. Tested duplicate-message idempotency.
9. Tested no-free-slot behavior.
10. Tested Task 1 → reflection → adaptive Task 2 behavior.
11. Compiled the Python source tree.

## Automated result

```text
24 tests passed
1 non-blocking Starlette deprecation warning
```

The warning comes from Starlette's current `TestClient` type alias and does not affect runtime behavior.

## Offline Deep Agent trace

```text
read_file(learning-arc-tutor/SKILL.md)
create_notion_page("RAG — first arc") -> notion-page-1
find_free_slot("Asia/Kolkata") -> 2026-09-15T18:30:00+05:30
create_calendar_event(...) -> calendar-event-1
final -> "Created one adaptive lesson in Notion and scheduled a confirmed free slot."
```

This test uses the real Deep Agents execution loop with scripted model decisions and fake external tool implementations. It proves agent/tool orchestration without pretending that remote objects exist.

## Docker verification

The Docker deployment was exercised on Docker 29.1.3 with Compose 2.40.3:

- `docker compose config --quiet` passed;
- the `learning-arc:local` image built successfully;
- importing the packaged FastAPI app inside the image returned `Learning Arc`;
- a container started in mock mode and reported healthy application startup;
- `GET /health` through the published port returned `{"status":"ok","mode":"mock"}`;
- the smoke-test container was removed afterward.

The Compose port is bound to `127.0.0.1:8000`, and `.env` is excluded from both Git and the Docker build context.

## Lemma verification

- Installed `uselemma-tracing` 7.11.2 with its LangGraph integration.
- Constructed the official `LemmaLangChainCallbackHandler` successfully.
- Verified that each Learning Arc execution attaches one callback to the Deep Agent graph invocation.
- Verified propagation of the Discord message ID as `thread_id` and Discord learner ID as `user_id`.
- Rebuilt the Docker image and imported Lemma's LangGraph adapter inside the container.

A ready remote Lemma trace still requires `LEMMA_API_KEY` and `LEMMA_PROJECT_ID`; the dashboard trace must be inspected after those values are supplied.

## What could not be executed

The machine currently has none of these configured:

- `COMPOSIO_API_KEY`
- `OPENROUTER_API_KEY`
- `DISCORD_BOT_TOKEN`
- a project `.env`

The Composio dashboard redirects to its sign-in page, so Notion, Google Calendar, and Google Tasks accounts are not connected. Live execution cannot be completed without the account owner authenticating. No remote success is claimed.

## External-app count

The required configuration uses three external apps:

1. Discord — receives the learner request and posts the result.
2. Notion — stores the learning arc and current lesson.
3. Google Calendar — checks availability and schedules the session.

Optional fourth app:

4. Google Tasks — creates the one current action and later supplies a completion signal.

## Final live test checklist

- [ ] Add keys to `.env` locally.
- [ ] Connect Notion in Composio.
- [ ] Connect Google Calendar in Composio.
- [ ] Optionally connect Google Tasks and set `ENABLE_GOOGLE_TASKS=true`.
- [ ] Add the Discord bot token and enable Message Content intent.
- [ ] Run FastAPI and the Discord bot.
- [ ] Send the demo `!learn` command.
- [ ] Verify returned Notion, Calendar, and optional Tasks object IDs directly in each app.
- [ ] Repeat the Discord message ID and verify no duplicates.
- [ ] Capture the action trace for the README and demo.
