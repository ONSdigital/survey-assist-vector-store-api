"""Tests for the main FastAPI application."""

from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from survey_assist_vector_store_api.shared.fastapi_app import AppMetadata
from survey_assist_vector_store_api.vector_store_api import main as main_module
from tests.helpers import assert_registered_generic_error_handler, create_test_app


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
    app = create_test_app(
        main_module,
        metadata=AppMetadata(
            title="Test API",
            description="Test description",
            version="9.9.9",
            root_message="Test API is running",
        ),
        lifespan=main_module.vector_store_lifespan,
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
def test_create_app_uses_metadata_helpers_by_default() -> None:
    """Verify that create_app uses the module defaults when overrides are absent."""
    app = create_test_app(main_module, lifespan=main_module.vector_store_lifespan)

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": main_module.DEFAULT_ROOT_MESSAGE}
    assert app.title == main_module.DEFAULT_APP_TITLE
    assert app.description == main_module.DEFAULT_APP_METADATA.description
    assert app.version == main_module.API_PACKAGE_VERSION


@pytest.mark.api
def test_generic_error_handler_returns_generic_500(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that create_app registers the expected generic 500 handler."""
    assert_registered_generic_error_handler(
        monkeypatch,
        app=create_test_app(
            main_module,
            lifespan=main_module.vector_store_lifespan,
        ),
        logger=main_module.logger,
    )
