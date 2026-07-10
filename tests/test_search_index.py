"""Tests for the search-index route."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from survey_assist_embed_core.models import SearchIndexItem, SearchIndexResponse

from survey_assist_vector_store_api.api import lifespan as lifespan_module
from survey_assist_vector_store_api.api.main import create_app


class FakeEmbeddingHandler:  # pylint: disable=too-few-public-methods
    """Simple test double for the embed-core handler."""

    def __init__(self, response: SearchIndexResponse | None = None):
        """Initialise the fake handler with a deterministic response."""
        self.calls: list[list[str]] = []
        self._response = response or SearchIndexResponse(
            results=[
                SearchIndexItem(
                    distance=0.1,
                    title="Software developer",
                    code="1234",
                )
            ]
        )

    def search_index_multi(self, query: list[str | None]) -> SearchIndexResponse:
        """Record query inputs and return the configured fake response."""
        self.calls.append([value for value in query if value is not None])
        return self._response


@pytest.mark.api
def test_search_index_route_uses_handler_from_request_state(
    create_app_with_handler,
) -> None:
    """Verify that the route reads the startup-loaded handler from request state."""
    fake_handler = FakeEmbeddingHandler()
    app = create_app_with_handler(fake_handler)

    with TestClient(app) as client:
        response = client.post(
            "/v1/search-index",
            json={"query": ["information", "software developer"]},
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "results": [
            {
                "distance": 0.1,
                "title": "Software developer",
                "code": "1234",
            }
        ]
    }
    assert fake_handler.calls == [["information", "software developer"]]


@pytest.mark.api
def test_search_index_route_validates_query_payload(
    create_app_with_handler,
) -> None:
    """Verify that malformed request payloads are rejected by FastAPI."""
    fake_handler = FakeEmbeddingHandler()
    app = create_app_with_handler(fake_handler)

    with TestClient(app) as client:
        response = client.post(
            "/v1/search-index",
            json={"query": "software developer"},
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert not fake_handler.calls


@pytest.mark.api
def test_create_app_loads_handler_on_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that the concrete app constructs the handler during startup."""
    fake_handler = FakeEmbeddingHandler()
    settings_marker = object()
    seen_settings: list[object] = []

    def fake_get_settings() -> object:
        return settings_marker

    def fake_load_embedding_handler(settings: object) -> FakeEmbeddingHandler:
        seen_settings.append(settings)
        return fake_handler

    monkeypatch.setattr(lifespan_module, "get_settings", fake_get_settings)
    monkeypatch.setattr(
        lifespan_module,
        "load_embedding_handler",
        fake_load_embedding_handler,
    )

    app = create_app()

    with TestClient(app) as client:
        response = client.post("/v1/search-index", json={"query": ["developer"]})

    assert response.status_code == status.HTTP_200_OK
    assert seen_settings == [settings_marker]
    assert fake_handler.calls == [["developer"]]
