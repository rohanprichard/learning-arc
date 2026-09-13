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
6. Tested Discord command parsing and response formatting.
7. Tested duplicate-message idempotency.
8. Tested no-free-slot behavior.
9. Tested Task 1 → reflection → adaptive Task 2 behavior.
10. Compiled the Python source tree.

## Automated result

```text
17 tests passed
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
