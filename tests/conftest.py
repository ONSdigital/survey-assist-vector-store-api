"""Shared pytest fixtures for API route tests."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI

from survey_assist_vector_store_api.api import main as main_module
from survey_assist_vector_store_api.api.main import create_app


@pytest.fixture(name="create_app_with_handler")
def create_app_with_handler_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[object], FastAPI]:
    """Return an app factory whose lifespan exposes the provided handler."""

    def _create_app_with_handler(handler: object) -> FastAPI:
        @asynccontextmanager
        async def lifespan_context(
            _app: FastAPI,
        ) -> AsyncIterator[dict[str, object]]:
            yield {"embedding_handler": handler}

        monkeypatch.setattr(main_module, "vector_store_lifespan", lifespan_context)
        return create_app()

    return _create_app_with_handler
