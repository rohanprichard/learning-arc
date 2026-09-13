# Learning Arc — adaptive learning connected to real life

## One-sentence pitch

**Learning Arc takes Bloom Tutor beyond the terminal: a learner starts in Discord, receives one adaptive task in Notion, gets a conflict-checked study session in Google Calendar, and unlocks an evidence-driven next task after reflecting on what actually happened.**

## The human moment

> “I want to build a small RAG demo. I know Python, but I only have Tuesday and Thursday evenings.”

Learning Arc does not return a twelve-week curriculum. It produces one bounded task, places it in the learner's tools, and finds a real moment to begin.

> “Start with one 35-minute retrieval experiment. Your task is in Notion and Tuesday's free slot is on your Calendar. Tell me what failed, and I will shape the next step around it.”

## Why the name

An **arc** is both a geometric curve and a trajectory over time. A rigid plan is a straight line; real learning bends around work, confusion, missed sessions, and new evidence. The name is short, visual, and compatible with the existing Bloom identity.

**Recommended brand:** **Learning Arc**  
**Tagline:** *Learning that bends around your life.*

## Related name directions

### Geometry and trajectory

- **Learning Arc** — warm, visual, and directly connected to adaptive progress.
- **Arcway** — a guided path with a softer product feel.
- **Arcline** — a visible trajectory from intent to capability.
- **Trajectory** — technically strong, but colder and harder to say.
- **Vector** — direction plus magnitude; better for a technical audience.
- **Waypoint** — every task is a reachable point on the path.
- **Orbit** — Bloom stays around the learner across their tools.
- **Tangent** — each task meets the learner exactly where they are; clever but abstract.
- **Parabola** — memorable geometry, though less emotionally intuitive.

### Warm momentum

- **Morrow** — tomorrow made concrete.
- **Rill** — a small stream that keeps moving.
- **Tend** — patient, caring progress.
- **Steady** — guilt-free momentum that fits real life.
- **Sprig** — a small beginning with room to grow.
- **Aster** — warm botanical continuity with Bloom.
- **Forth** — concise and active.
- **Driftwood** — organic progress, but too passive for the product.

### Final shortlist

1. **Learning Arc** — best balance of attribution, warmth, story, and visual identity.
2. **Bloom Orbit** — strongest multi-app metaphor.
3. **Arcway** — strongest standalone product name.
4. **Morrow** — warmest standalone brand.
5. **Rill** — most distinctive warm name.

## What comes from Bloom Tutor

Bloom Tutor already provides the pedagogical core:

- one syllabus with measurable mastery outcomes;
- exactly one lesson at a time;
- learner questions and inline feedback;
- an adaptive next lesson based on that evidence;
- a final evaluation and summary.

Learning Arc should preserve that core rather than turning it into a generic planner. For the English hackathon demo, the implementation uses a small English `sprint` adaptation: 3–5 measurable outcomes and one 15–45 minute task.

## App responsibilities

| App | Responsibility | Visible state change |
|---|---|---|
| Discord | Intent, approval, reflection, and honest status | Learner receives the task, links, and partial-failure state |
| Notion | Syllabus, current lesson, reflection, and progress | One page is created and then appended with Task 2 |
| Google Calendar | Real availability and study commitment | A free slot is found before one event is created |
| Google Tasks | Optional fourth app and completion surface | One current task links to the Notion lesson |
| YouTube | Optional references after the core is live | Two bounded references or an actual playlist |

## Technical architecture

Use **Python and FastAPI** with a real LangChain **Deep Agent**:

- `discord.py` receives the learner's message;
- FastAPI exposes the agent endpoint and visible run receipts;
- Deep Agents supplies the reasoning → tool call → observation → recovery loop;
- the Bloom-derived Agent Skill is loaded progressively from `skills/`;
- Composio supplies Notion and Google Calendar router tools and OAuth;
- Lemma's LangGraph callback records one complete trace per agent execution, including model generations and tool results;
- deterministic Python provides a stable thread ID, idempotency cache, and exact tool allowlists.

This is not a fixed automation pretending to be an agent. The model decides the smallest credible lesson, discovers the allowed tool schemas, selects and calls tools, observes success or failure, and changes its next action from that observation. The deterministic shell constrains the agent; it does not replace its reasoning.

Lemma is not counted as one of the three required end-user apps. It is the evidence layer that lets judges inspect the full agent trajectory and verify that Learning Arc did not invent successful writes or ignore tool failures.

## Primary flow

1. The learner sends `!learn topic | goal | availability | timezone` in Discord.
2. Learning Arc generates 3–5 measurable mastery outcomes and exactly one first task.
3. It creates one Notion topic page with the current task.
4. It asks Google Calendar for a free slot inside the allowed study window.
5. It creates one 35-minute event only when a slot exists.
6. Discord receives the next action, time, links, and run ID.
7. The learner submits a reflection after the task.
8. Learning Arc generates exactly one adaptive Task 2, appends it to Notion, and schedules the next free session.

## The key adaptive demo

Task 1:

> Run retrieval over five notes and label one useful and one poor result.

Learner reflection:

> The relevant notes appeared, but every chunk was too broad.

Adaptive Task 2:

> Compare two chunk sizes using the same five questions and record whether precision improves.

This demonstrates adaptation from evidence rather than merely revealing a prewritten lesson.

## Reliability contract

- A Discord message ID is the idempotency key.
- The same request cannot create duplicate pages or events.
- Calendar availability is checked before any event write.
- No free slot means `needs_scheduling`; no time is invented.
- A failed tool produces visible partial state rather than a false success.
- The model writes lesson content but cannot choose arbitrary external tools.
- Only four Composio tools are allowed for the MVP.

## MVP and stretch line

### Must work

- Discord input and response.
- Notion page creation.
- Calendar free-slot check and event creation.
- One completion reflection producing Task 2.
- Duplicate request and full-calendar tests.

### Stretch

- Google Tasks as the easiest fourth app and completion signal.
- YouTube reference search or playlist creation.
- Scheduled pre-session reminders.
- Notion completion webhook.
- Persistent multi-user course history.
- Deep Agents memory or subagents.

## Two-minute demo

### 0:00–0:12 — problem

“Learning plans usually fail between wanting to learn and knowing what to do tonight.”

### 0:12–0:28 — request

Send the RAG request in Discord.

### 0:28–0:58 — action across apps

Show one Notion page and one conflict-checked Calendar event, then return to the Discord action receipt.

### 0:58–1:22 — the first attainable task

Open the Notion task and show its success criteria and 35-minute boundary.

### 1:22–1:43 — adaptation

Submit the chunk-size reflection. Show Task 2 change and the next Calendar event.

### 1:43–1:54 — reliability

Repeat the initial Discord message ID or run the duplicate fixture. Show the same run ID and zero duplicate writes.

### 1:54–2:00 — close

“Learning Arc does not just design a learning path. It bends the next step around your life and what you actually learned.”

## Build status

The repository currently contains a working FastAPI mock flow, Discord command adapter, structured Bloom planner adapter, Composio gateway, explicit tool allowlist, and automated tests. Live Notion and Calendar writes still require the learner's Composio-connected accounts and must not be claimed until exercised.

## References

- Hackathon: https://multiappagenthackathon.com/
- Bloom Tutor: https://github.com/Li-Evan/Bloom
- Composio + LangChain: https://docs.langchain.com/oss/python/integrations/tools/composio
- Composio Notion toolkit: https://docs.composio.dev/toolkits/notion
- Composio Google Calendar toolkit: https://docs.composio.dev/toolkits/googlecalendar
- Deep Agents overview: https://docs.langchain.com/oss/python/deepagents/overview
