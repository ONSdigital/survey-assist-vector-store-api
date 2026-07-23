"""Tests for the SAYT configuration route."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from survey_assist_embed_core.sayt.core import (
    SaytArtifactProvenance,
    SaytConfiguration,
    SaytCorpusSummary,
    SaytGlobalSettings,
    SaytRetrieverArtifactProvenance,
    SaytRetrieverSummary,
)


class FakeSuggester:  # pylint: disable=too-few-public-methods
    """Simple test double exposing a fixed configuration."""

    def __init__(self) -> None:
        """Initialise the fake suggester with deterministic configuration."""
        self.calls = 0
        self._config = SaytConfiguration(
            settings=SaytGlobalSettings(min_chars=2, max_suggestions=10),
            corpus=SaytCorpusSummary(
                size=120,
                unique_display_texts=100,
                max_duplication=4,
            ),
            retrievers=[
                SaytRetrieverSummary(
                    name="prefix",
                    spec_type="prefix",
                    retriever_type="PrefixRetriever",
                    configured_weight=1.0,
                    normalised_weight=0.6,
                    config={"min_prefix_len": 2},
                    artifact_provenance=SaytRetrieverArtifactProvenance(
                        artifact_type="prefix_index",
                        path="artifacts/prefix.json",
                        config={"format": "json"},
                    ),
                )
            ],
            artifact_provenance=SaytArtifactProvenance(
                artifact_dir="artifacts/sayt",
                artifact_type="sayt_artifact",
                artifact_version=1,
                corpus_file="corpus.csv",
                corpus_size=120,
            ),
        )

    def get_config(self) -> SaytConfiguration:
        """Record access and return the configured metadata."""
        self.calls += 1
        return self._config


@pytest.mark.api
def test_configuration_route_returns_suggester_configuration(
    create_sayt_app_with_suggester,
) -> None:
    """Verify that the route returns the loaded suggester configuration."""
    fake_suggester = FakeSuggester()
    app = create_sayt_app_with_suggester(fake_suggester)

    with TestClient(app) as client:
        response = client.get("/v1/configuration")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "settings": {"min_chars": 2, "max_suggestions": 10},
        "corpus": {
            "size": 120,
            "unique_display_texts": 100,
            "max_duplication": 4,
        },
        "retrievers": [
            {
                "name": "prefix",
                "spec_type": "prefix",
                "retriever_type": "PrefixRetriever",
                "configured_weight": 1.0,
                "normalised_weight": 0.6,
                "config": {"min_prefix_len": 2},
                "artifact_provenance": {
                    "artifact_type": "prefix_index",
                    "path": "artifacts/prefix.json",
                    "config": {"format": "json"},
                },
            }
        ],
        "artifact_provenance": {
            "artifact_dir": "artifacts/sayt",
            "artifact_type": "sayt_artifact",
            "artifact_version": 1,
            "corpus_file": "corpus.csv",
            "corpus_size": 120,
        },
    }
    assert fake_suggester.calls == 1
