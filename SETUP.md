# Learning Arc setup

## 1. Discord

1. Open https://discord.com/developers/applications and select **New Application**.
2. Name it **Learning Arc**.
3. Open **Bot** in the left sidebar.
4. Under **Token**, choose **Reset Token**, copy the token, and keep it private.
5. Under **Privileged Gateway Intents**, enable **Message Content Intent**. Presence and Server Members intents are not required.
6. Open **Installation**.
7. Enable **Guild Install** and use the Discord-provided install link.
8. Under the guild-install defaults, add the `bot` scope and only these permissions:
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Read Message History
   - Embed Links
9. Copy the installation link, open it, and add Learning Arc to a test server you control.
10. Give the bot access to the demo channel. Do not grant Administrator.

Learning Arc uses Discord's Gateway connection, so you do not need an Interaction Endpoint URL, slash command, or ngrok tunnel.

## 2. Composio

1. Open https://dashboard.composio.dev and create or select a project.
2. Open **Settings → API Keys** and create/copy a project API key.
3. Create a blank Notion page named **Learning Arc Demo**. This gives the agent a safe parent area.
4. In Composio, connect these toolkits using managed OAuth:
   - **Notion** — during authorization, grant access to the `Learning Arc Demo` page.
   - **Google Calendar** — authorize the Google account/calendar used for the demo.
   - **Google Tasks** — authorize the same Google account if the optional fourth app is enabled.
5. If Composio asks for an entity/user ID, enter `demo-user`, which matches Learning Arc's default session user.
6. Confirm each connected account shows as active before recording the demo.

Composio supplies the OAuth applications for these toolkits, so you do not need to create separate Notion or Google Cloud OAuth clients.

## 3. OpenRouter

1. Open https://openrouter.ai/settings/keys.
2. Create an API key with enough credit for the demo.
3. Learning Arc defaults to `deepseek/deepseek-v4.1-flash`; no model setting is required.

## 4. Configure Learning Arc

Edit `/home/roh/learning-arc/.env`:

```dotenv
COMPOSIO_API_KEY=your_composio_key
OPENROUTER_API_KEY=your_openrouter_key
DISCORD_BOT_TOKEN=your_discord_bot_token
ENABLE_GOOGLE_TASKS=true
```

Do not post this file or its values in Discord. `.env` is excluded from Git and the Docker build context.

Lemma support is already installed and wired, but it remains disabled when `LEMMA_API_KEY` and `LEMMA_PROJECT_ID` are absent.

## 5. Start everything

```bash
cd /home/roh/learning-arc && ./run.sh
```

The one launcher validates credentials, builds the Docker image, and starts FastAPI plus the Discord Gateway bot.

## 6. Verify

1. Confirm the logs contain `Learning Arc connected as ...` and FastAPI startup success.
2. In a DM, send an ordinary message such as:

   > I want to learn RAG for a small project. I know Python, and Tuesday evening usually works for me.

3. In a server, mention `@Learning Arc` once to start. Follow-up replies need no mention or special syntax.
4. If information is missing, verify that the bot asks one natural question instead of writing incomplete app state.
5. After sufficient context, verify directly:
   - the Notion page exists;
   - the Calendar event occupies a genuinely free slot;
   - the optional Google Task links back to Notion;
   - Discord contains the action receipt and object links.
6. Repeat the same delivered message ID in the test harness and confirm no duplicate app writes.

Stop with `Ctrl+C`. To remove the container afterward:

```bash
cd /home/roh/learning-arc && docker compose down
```
