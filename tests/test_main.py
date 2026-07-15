"""Tests for the main FastAPI application."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

from survey_assist_vector_store_api.vector_search_api import main as main_module
from survey_assist_vector_store_api.vector_search_api.main import create_app


@pytest.fixture(name="fake_lifespan")
def fake_lifespan_fixture(monkeypatch: pytest.MonkeyPatch):
    """Patch the concrete app lifespan so tests do not load a real vector store."""

    async def _empty_lifespan(_app: FastAPI):
        yield {}

    patched_lifespan = asynccontextmanager(_empty_lifespan)
    monkeypatch.setattr(main_module, "vector_store_lifespan", patched_lifespan)
    return patched_lifespan


@pytest.mark.api
@pytest.mark.usefixtures("fake_lifespan")
def test_create_app_applies_overrides_to_app_and_root_route() -> None:
    """Verify that create_app applies configuration overrides to the app."""
    app = create_app(
        title="Test API",
        description="Test description",
        version="9.9.9",
        root_message="Test API is running",
    )

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Test API is running"}
    assert app.title == "Test API"
    assert app.description == "Test description"
    assert app.version == "9.9.9"


@pytest.mark.api
@pytest.mark.usefixtures("fake_lifespan")
def test_create_app_uses_metadata_helpers_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that create_app delegates default metadata and version resolution."""
    monkeypatch.setattr(
        main_module,
        "build_default_app_description",
        lambda *, description: "API versions: api=1.2.3, embed_core=4.5.6",
    )
    monkeypatch.setattr(main_module, "API_PACKAGE_VERSION", "1.2.3")

    app = create_app()

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Vector Store API is running"}
    assert app.title == "Vector Store API"
    assert app.description == "API versions: api=1.2.3, embed_core=4.5.6"
    assert app.version == "1.2.3"


@pytest.mark.api
def test_generic_error_handler_returns_generic_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that create_app registers the expected generic 500 handler."""
    logged_messages: list[tuple[str, dict[str, str]]] = []
    request = Request({"type": "http", "headers": []})
    app = create_app()

    def fake_error(message: str, **kwargs: str) -> None:
        logged_messages.append((message, kwargs))

    monkeypatch.setattr(main_module.logger, "error", fake_error)

    response = asyncio.run(
        app.exception_handlers[Exception](request, RuntimeError("boom"))
    )

    assert len(logged_messages) == 1
    message, kwargs = logged_messages[0]
    assert message == "Unexpected error"
    assert kwargs["error"] == "boom"
    assert kwargs["error_type"] == "RuntimeError"
    assert "RuntimeError: boom" in kwargs["traceback"]
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.body == b'{"detail":"An unexpected error occurred"}'
