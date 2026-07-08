"""Application lifespan helpers for the vector-store API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from survey_assist_vector_store_api.api.deps.settings import get_settings
from survey_assist_vector_store_api.api.deps.vector_store import build_embedding_handler


@asynccontextmanager
async def vector_store_lifespan(_app: FastAPI) -> AsyncIterator[dict[str, object]]:
    """Load the embedding handler once and expose it through request state."""
    settings = get_settings()
    handler = build_embedding_handler(settings)
    yield {
        "settings": settings,
        "embedding_handler": handler,
    }
