"""Tests for the runtime-config route."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from survey_assist_embed_core.models import EmbeddingStatus, VectorBackendConfig


class FakeEmbeddingHandler:  # pylint: disable=too-few-public-methods
    """Simple test double exposing a fixed runtime configuration."""

    def __init__(self):
        """Initialise the fake handler with deterministic configuration."""
        self.calls = 0
        self._config = EmbeddingStatus(
            db_dir="vector_store",
            k_matches=20,
            index_source_file="gs://bucket/source.csv",
            backend=VectorBackendConfig(
                backend_name="classifai",
                settings={
                    "embedding_model_name": ("sentence-transformers/all-MiniLM-L6-v2")
                },
            ),
            index_size=10,
            status="ready",
        )

    def get_embed_config(self) -> EmbeddingStatus:
        """Record access and return the configured runtime metadata."""
        self.calls += 1
        return self._config


@pytest.mark.api
def test_runtime_config_route_returns_handler_configuration(
    create_app_with_handler,
) -> None:
    """Verify that the route returns the loaded handler runtime config."""
    fake_handler = FakeEmbeddingHandler()
    app = create_app_with_handler(fake_handler)

    with TestClient(app) as client:
        response = client.get("/v1/runtime-config")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "db_dir": "vector_store",
        "k_matches": 20,
        "index_source_file": "gs://bucket/source.csv",
        "backend": {
            "backend_name": "classifai",
            "settings": {
                "embedding_model_name": "sentence-transformers/all-MiniLM-L6-v2"
            },
        },
        "index_size": 10,
        "status": "ready",
    }
    assert fake_handler.calls == 1
