FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.4.1 \
    POETRY_NO_INTERACTION=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app

FROM base AS deps

COPY pyproject.toml poetry.lock README.md ./
COPY src ./src

RUN poetry install --only main --no-ansi

FROM deps AS vector-search

EXPOSE 8088

CMD ["poetry", "run", "uvicorn", "survey_assist_vector_store_api.vector_search_api.main:app", "--host", "0.0.0.0", "--port", "8088"]

FROM deps AS sayt

EXPOSE 8089

CMD ["poetry", "run", "uvicorn", "survey_assist_vector_store_api.sayt_api.main:app", "--host", "0.0.0.0", "--port", "8089"]
