# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.12-slim-bookworm

FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    POETRY_VERSION=2.4.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_REQUESTS_MAX_RETRIES=5 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only main --no-root --no-ansi

COPY src ./src

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --only-root --no-ansi

FROM ${PYTHON_IMAGE} AS runtime-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH="/app/src"

WORKDIR /app

RUN useradd --system --create-home --home-dir /home/appuser \
    --shell /usr/sbin/nologin appuser

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

RUN chown -R appuser:appuser /app

USER appuser

FROM runtime-base AS vector-store

EXPOSE 8088

CMD ["uvicorn", "survey_assist_vector_store_api.vector_store_api.main:app", "--host", "0.0.0.0", "--port", "8088"]

FROM runtime-base AS sayt

EXPOSE 8090

CMD ["uvicorn", "survey_assist_vector_store_api.sayt_api.main:app", "--host", "0.0.0.0", "--port", "8090"]
