"""Tests for the SAYT FastAPI application."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

from survey_assist_vector_store_api.sayt_api import main as main_module
from survey_assist_vector_store_api.sayt_api.main import create_app


@pytest.fixture(name="fake_sayt_lifespan")
def fake_sayt_lifespan_fixture(monkeypatch: pytest.MonkeyPatch):
    """Patch the concrete SAYT lifespan so tests do not load a real artifact."""

    async def _empty_lifespan(_app: FastAPI):
        yield {}

    patched_lifespan = asynccontextmanager(_empty_lifespan)
    monkeypatch.setattr(main_module, "sayt_lifespan", patched_lifespan)
    return patched_lifespan


@pytest.mark.api
@pytest.mark.usefixtures("fake_sayt_lifespan")
def test_create_app_applies_overrides_to_app_and_root_route() -> None:
    """Verify that create_app applies configuration overrides to the app."""
    app = create_app(
        title="Test SAYT API",
        description="Test SAYT description",
        version="9.9.9",
        root_message="Test SAYT API is running",
    )

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Test SAYT API is running"}
    assert app.title == "Test SAYT API"
    assert app.description == "Test SAYT description"
    assert app.version == "9.9.9"


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
