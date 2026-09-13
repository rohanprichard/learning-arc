#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env. Add the three credentials, then run ./run.sh again."
  exit 1
fi

set -a
source .env
set +a

missing=()
for key in COMPOSIO_API_KEY OPENROUTER_API_KEY DISCORD_BOT_TOKEN LEMMA_API_KEY LEMMA_PROJECT_ID; do
  if [[ -z "${!key:-}" ]]; then
    missing+=("$key")
  fi
done
if (( ${#missing[@]} )); then
  printf 'Missing values in .env: %s\n' "${missing[*]}"
  exit 1
fi

run_compose() {
  docker compose up --build
}

if docker info >/dev/null 2>&1; then
  run_compose
else
  exec sg docker -c "cd '$PWD' && docker compose up --build"
fi
