"""Tests for the main FastAPI application."""

import asyncio
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

from survey_assist_vector_store_api.api import main as main_module
from survey_assist_vector_store_api.api.main import create_app


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
        "resolve_app_metadata",
        lambda *, title, description, root_message: (
            "SIC Vector Store API",
            "API for interacting with the SIC vector store",
            "SIC Vector Store API is running",
        ),
    )
    monkeypatch.setattr(
        main_module,
        "resolve_default_version",
        lambda: "1.2.3",
    )

    app = create_app()

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "SIC Vector Store API is running"}
    assert app.title == "SIC Vector Store API"
    assert app.description == "API for interacting with the SIC vector store"
    assert app.version == "1.2.3"


@pytest.mark.api
def test_generic_error_handler_returns_generic_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the generic exception handler returns the expected 500 body."""
    printed: list[str] = []
    request = Request({"type": "http", "headers": []})

    def fake_print(message: str) -> None:
        printed.append(message)

    monkeypatch.setattr("builtins.print", fake_print)

    response = asyncio.run(
        main_module.generic_error_handler(request, RuntimeError("boom"))
    )

    assert printed == ["Unexpected error: boom"]
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.body == b'{"detail":"An unexpected error occurred"}'
