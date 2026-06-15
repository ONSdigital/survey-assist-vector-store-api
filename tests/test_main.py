"""Tests for the main FastAPI application."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from survey_assist_vector_store_api.api.main import create_app


@pytest.mark.api
def test_root_endpoint_returns_configured_message() -> None:
    """Verify that the root endpoint returns the configured message.

    Tests that the root endpoint ("/") returns a 200 status code and a
    JSON response containing the message that was configured during app
    initialisation.
    """
    app = create_app(root_message="Test API is running")

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Test API is running"}


@pytest.mark.api
def test_lifespan_startup_and_shutdown_hooks_are_called() -> None:
    """Verify that application lifecycle hooks are invoked correctly.

    Tests that the startup hook is called when the application initialises
    and the shutdown hook is called when the application terminates, ensuring
    that both hooks are executed in the correct order.
    """
    events: list[str] = []

    def startup_hook(_app) -> None:
        events.append("startup")

    def shutdown_hook(_app) -> None:
        events.append("shutdown")

    app = create_app(
        startup_hook=startup_hook,
        shutdown_hook=shutdown_hook,
    )

    with TestClient(app) as client:
        assert client.get("/").status_code == status.HTTP_200_OK
        assert events == ["startup"]

    assert events == ["startup", "shutdown"]
