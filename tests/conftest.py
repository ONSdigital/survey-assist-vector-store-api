"""Shared pytest fixtures for API route tests."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI

from survey_assist_vector_store_api.sayt_api import main as sayt_main_module
from survey_assist_vector_store_api.vector_search_api import main as main_module
from tests.helpers import create_test_app


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
        return create_test_app(
            main_module,
            lifespan=main_module.vector_store_lifespan,
        )

    return _create_app_with_handler


@pytest.fixture(name="create_sayt_app_with_suggester")
def create_sayt_app_with_suggester_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[object], FastAPI]:
    """Return a SAYT app factory whose lifespan exposes the provided suggester."""

    def _create_sayt_app_with_suggester(suggester: object) -> FastAPI:
        @asynccontextmanager
        async def lifespan_context(
            _app: FastAPI,
        ) -> AsyncIterator[dict[str, object]]:
            yield {"suggester": suggester}

        monkeypatch.setattr(sayt_main_module, "sayt_lifespan", lifespan_context)
        return create_test_app(
            sayt_main_module,
            lifespan=sayt_main_module.sayt_lifespan,
        )

    return _create_sayt_app_with_suggester
