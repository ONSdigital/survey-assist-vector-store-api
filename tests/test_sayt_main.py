"""Tests for the SAYT FastAPI application."""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from survey_assist_vector_store_api.sayt_api import main as main_module
from survey_assist_vector_store_api.shared.fastapi_app import AppMetadata
from tests.helpers import assert_registered_generic_error_handler, create_test_app


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
    app = create_test_app(
        main_module,
        metadata=AppMetadata(
            title="Test SAYT API",
            description="Test SAYT description",
            version="9.9.9",
            root_message="Test SAYT API is running",
        ),
        lifespan=main_module.sayt_lifespan,
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
    assert_registered_generic_error_handler(
        monkeypatch,
        app=create_test_app(
            main_module,
            lifespan=main_module.sayt_lifespan,
        ),
        logger=main_module.logger,
    )
