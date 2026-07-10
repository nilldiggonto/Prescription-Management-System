# Backend application image only — no PostgreSQL container in here.
# Point DATABASE_URL (and the rest of backend/.env) at a Postgres instance you run separately.

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# argon2-cffi/asyncpg build C extensions during `uv sync` on some platforms — build-essential
# is only needed in this stage, not in the final image.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (cached separately from app code) using the lockfile as-is.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Applies pending Alembic migrations, then starts the API. `backend/.env` (or equivalent
# env vars passed to `docker run`) must be present — see backend/.env.example.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
