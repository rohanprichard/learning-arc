FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra agent --no-install-project

COPY README.md ./
COPY src ./src
COPY skills ./skills
RUN uv sync --frozen --no-dev --extra agent

EXPOSE 8000

CMD ["python", "-m", "bloom_arc"]
