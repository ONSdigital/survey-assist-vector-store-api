"""Application lifespan helpers for the SAYT API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from survey_assist_vector_store_api.sayt_api.deps.settings import get_settings
from survey_assist_vector_store_api.sayt_api.deps.suggester import load_suggester


@asynccontextmanager
async def sayt_lifespan(_app: FastAPI) -> AsyncIterator[dict[str, object]]:
    """Load the SAYT suggester once and expose it through request state."""
    settings = get_settings()
    suggester = load_suggester(settings)
    yield {
        "suggester": suggester,
    }
